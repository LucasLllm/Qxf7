from pathlib import Path
import csv,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from compare_uiuc import surfaces,parse_points
D=Path(__file__).resolve().parent
C=np.load(D/'uiuc-comparison/corpus.npz');G=C['grid'];N=C['names'].tolist()
R=list(csv.DictReader((D/'uiuc-comparison/uiuc_matches.csv').open()))
keys=['wing_root.dat','inner_clean.dat','outer_clean.dat','root_140cosineSelig.dat']
fig,axs=plt.subplots(4,1,figsize=(11,10))
for ax,key in zip(axs,keys):
 r=next(q for q in R if q['rank']=='1' and Path(q['profile']).name==key)
 u,l=surfaces(parse_points((D/r['profile']).read_text()));i=N.index(r['uiuc_member'])
 for a in [u,l]:ax.plot(G,a,'b',lw=1,label='extracted' if a is u else None)
 for j,a in enumerate([C['upper'][i],C['lower'][i]]):ax.plot(G,a,'r--',lw=.9,label=Path(r['uiuc_member']).name if j==0 else None)
 ax.set_title(key+'; RMS '+format(float(r['rms_ordinate_deviation_percent_chord']),'.3f')+'% chord')
 ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(loc='upper right');ax.set_ylabel('y/c')
axs[-1].set_xlabel('x/c; source pose with declared gap closure; shape match is not identification')
fig.tight_layout();fig.savefig(D/'uiuc-comparison/profile_match_review.png',dpi=180)
print('Wrote four-profile shape review')
