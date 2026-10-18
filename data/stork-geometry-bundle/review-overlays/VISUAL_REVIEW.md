# Parent visual review of extraction overlays

Reviewed `top_outline_overlay.png`, `front_outline_overlay.png`, `side_outline_overlay.png` using native image inspection after the renderer exited0.

- Axes are explicitly labelled in common original STEP frame: x aft, y right, z up, millimetres. The top view intentionally puts longitudinal x on vertical plot axis (nose at bottom); do not read as a conventional north-up map.
- Top/front views are visually bilateral; wing and tail roots are located at the fuselage, with no obvious gross axis permutation or scaling errors. This is a visualization sanity check, not independent registration proof.
- Side view separately and legibly dimensions nose-to-pusher1000.00mm and nose-to-fixed-tail aft1044.02mm. Both terminate at separate known extents, not the same pusher plane.
- Only registered fixed parts, controls and selected mounts/landing gear appear. Missing motors, carbon booms, propellers and unregistered printed fin-tip/hardware pieces are not drawn. No inferred hardware was added.
- The projected outlines are triangle-union silhouettes by component and category, not convex hull planforms. Small manufactured joints/recesses remain. Their dimensions are geometric saved-source results, not aircraft performance claims.
- Wings and rudders retain source control pose. These plots do not verify a commanded/aerodynamic neutral and do not establish flightworthiness.
