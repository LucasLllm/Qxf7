"""Import-safe APC computed map. No network, writes or extrapolation."""
from pathlib import Path
import math,re,bisect
ROOT=Path(__file__).resolve().parent

class DomainError(ValueError):
    """Requested point outside supported map or voltage envelope."""

def lerp(x,x0,x1,y0,y1):
    return y0+(y1-y0)*(x-x0)/(x1-x0)

class Propeller:
    def __init__(self,path=None):
        self.blocks={}
        for line in Path(path or ROOT/'data/PER3_10x6E.DOM.dat').read_text().splitlines():
            match=re.search(r'PROP RPM\s*=\s*(\d+)',line)
            if match:
                rpm=int(match[1]);self.blocks[rpm]=[];continue
            fields=line.split()
            if len(fields)==15:
                try: values=list(map(float,fields))
                except ValueError: continue
                self.blocks[rpm].append((values[0]*0.44704,values[10],values[8]))
        if not self.blocks: raise ValueError('no APC rows')
        self.rpms=sorted(self.blocks)

    def _slice(self,rpm,speed):
        rows=self.blocks[rpm]
        xs=[r[0] for r in rows]
        if not math.isfinite(speed) or speed<xs[0] or speed>xs[-1]:raise DomainError('airspeed outside RPM slice')
        i=bisect.bisect_left(xs,speed)
        if i<len(xs) and xs[i]==speed:return rows[i][1:]
        a,b=rows[i-1],rows[i]
        return tuple(lerp(speed,a[0],b[0],a[k],b[k]) for k in (1,2))

    def at(self,rpm,airspeed_mps):
        if not math.isfinite(rpm) or not self.rpms[0]<=rpm<=self.rpms[-1]:raise DomainError('RPM outside map')
        i=bisect.bisect_left(self.rpms,rpm)
        if self.rpms[i]==rpm:t,p=self._slice(rpm,airspeed_mps)
        else:
            lo,hi=self.rpms[i-1:i+1]
            a,b=self._slice(lo,airspeed_mps),self._slice(hi,airspeed_mps)
            t,p=(lerp(rpm,lo,hi,a[k],b[k]) for k in (0,1))
        return dict(rpm=rpm,airspeed_mps=airspeed_mps,thrust_N=t,shaft_W=p)

    def solve(self,thrust_N,airspeed_mps):
        if not math.isfinite(thrust_N) or thrust_N<=0:raise DomainError('positive finite thrust required')
        candidates=[]
        for rpm in self.rpms:
            try:candidates.append(self.at(rpm,airspeed_mps))
            except DomainError:continue
        for a,b in zip(candidates,candidates[1:]):
            # Both bounding slices must support this airspeed; no filling holes.
            if b['rpm']-a['rpm']!=1000:continue
            if a['thrust_N']<=thrust_N<=b['thrust_N'] and b['thrust_N']>a['thrust_N']:
                rpm=lerp(thrust_N,a['thrust_N'],b['thrust_N'],a['rpm'],b['rpm'])
                result=self.at(rpm,airspeed_mps)
                if result['shaft_W']<=0:raise DomainError('not a powered point')
                return result
        raise DomainError('thrust outside supported positive-thrust brackets')

def evaluate(thrust_N,airspeed_mps,loaded_voltage_V):
    """Conditional equivalent-DC motor predictions, NOT a calibrated ESC map.

    loaded_voltage_V is externally supplied pack-terminal voltage (10..16.8V).
    electrical_W excludes ESC, wiring, auxiliaries and battery internal losses.
    Infeasible cases retain predictions but MUST NOT be used as achieved power.
    """
    if not math.isfinite(loaded_voltage_V) or not 10<=loaded_voltage_V<=16.8:
        raise DomainError('4S loaded-voltage modeling interval is 10..16.8V, not a flight cutoff')
    result=Propeller().solve(thrust_N,airspeed_mps)
    rpm=result['rpm'];shaft=result['shaft_W'];emf=rpm/910
    if rpm>15000:raise DomainError('APC Thin Electric 150000/10 suggested RPM limit exceeded')
    cases=[]
    for factor in (0.5,1,2):
        resistance=0.072*factor
        for reference_V in (10,14):
            # Subtract no-load copper from Vref*I0; assume remaining drag/iron
            # power constant locally. This hypothesis is NOT a measured curve.
            reference_emf=reference_V-1.17*resistance
            no_load=reference_emf*1.17
            current=(shaft+no_load)/emf
            copper=current*current*resistance
            electrical=shaft+copper+no_load
            required=emf+resistance*current
            cases.append(dict(resistance_factor=factor,effective_R_ohm=resistance,
                idle_reference_V=reference_V,equivalent_motor_A=current,
                copper_W=copper,no_load_W=no_load,electrical_W=electrical,
                required_motor_V=required,voltage_feasible=required<=loaded_voltage_V,
                ideal_bus_A=electrical/loaded_voltage_V,
                ideal_pwm_duty=required/loaded_voltage_V))
    result.update(loaded_voltage_V=loaded_voltage_V,motor_cases=cases,
        electrical_model='uncalibrated equivalent-DC convention sensitivities; ESC excluded',
        all_cases_voltage_feasible=all(c['voltage_feasible'] for c in cases))
    return result

def integrate_curve(curve,cutoff_V):
    """Wh per cell from ordered (discharged Ah, loaded V) data; no extension.

    Stops at FIRST downward crossing. Does not qualify battery mission energy.
    """
    if not math.isfinite(cutoff_V) or len(curve)<2:raise DomainError('invalid curve or cutoff')
    if cutoff_V>curve[0][1]:raise DomainError('cutoff above curve start')
    energy=0.0
    for a,b in zip(curve,curve[1:]):
        if not all(math.isfinite(v) for v in (*a,*b)) or b[0]<=a[0]:raise DomainError('invalid curve ordering')
        if a[1]>=cutoff_V>=b[1]:
            endq=lerp(cutoff_V,a[1],b[1],a[0],b[0]) if a[1]!=b[1] else a[0]
            return energy+(endq-a[0])*(a[1]+cutoff_V)/2
        energy+=(b[0]-a[0])*(a[1]+b[1])/2
    raise DomainError('cutoff below captured curve: no extrapolation')

def energy_budget(source_usable_Wh,reserve_Wh,noncruise_Wh):
    """Explicit user-supplied reserve, NOT baked into usable Wh."""
    if not all(math.isfinite(v) and v>=0 for v in (source_usable_Wh,reserve_Wh,noncruise_Wh)):
        raise DomainError('finite nonnegative energies required')
    if reserve_Wh+noncruise_Wh>source_usable_Wh:raise DomainError('budget exceeds usable energy')
    return dict(source_usable_Wh=source_usable_Wh,reserve_Wh=reserve_Wh,
        noncruise_Wh=noncruise_Wh,cruise_Wh=source_usable_Wh-reserve_Wh-noncruise_Wh)
