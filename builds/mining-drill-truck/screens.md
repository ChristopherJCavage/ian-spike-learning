# Screens -- Mining Drill Truck

One row per Figma frame. Chrome: `context/instruction-screens.md`.

figma file: TBD

`camera` is either two LeoCAD angles (`lat lon`) or a `--viewpoint` name
(`front`, `back`, `left`, `right`, `top`, `home`). `--camera-angles` is
ignored when `--viewpoint` is set, so a page picks one. `highlight` is
whether LeoCAD should outline the parts added on that page.

Skid steer -- two Large Motors stand side by side under the Hub, each
spinning its own rear wheel directly off its output disc (no shared rear
axle). The front axle runs through a 5x7 frame pinned to the Hub's front
face (not hung on 3M pegs). The drill motor is pinned to a 7M beam on that
frame, and the distance sensor rides on two rails pinned to the Hub sides.
Cab decks are two plates pinned into the Hub's top holes. Check views
`renders/check-left.png`, `renders/check-front.png`, `renders/check-top.png`,
and `renders/check-iso.png` confirm: both rear discs drive their own wheel,
the front axle sits clear of the rear wheels, the drill bit clears the
front wheels, the sensor eyes are forward and above the wheel bottoms, the
5x7 frame clears the ground, and the minifig stands on the raised deck
facing the drill.

```
step | figma_frame | png | parts_added | camera | highlight | copy
1  | MiningDrillTruck/01-rear-motors   | renders/step-001.png | 2x Large Motor | 55 225 | yes | "Stand two motors side by side, discs facing out -- one for each rear wheel."
2  | MiningDrillTruck/02-rear-wheels   | renders/step-002.png | 2x 3M axle, 2x wheel | 55 225 | yes | "Push a short axle and a wheel onto each motor's disc."
3  | MiningDrillTruck/03-hub-pegs      | renders/step-003.png | 6x peg | 70 225 | yes | "Stand 6 pegs up across the motor tops -- leave the front pair empty."
4  | MiningDrillTruck/04-hub           | renders/step-004.png | 1x Hub | 55 225 | yes | "Lower the Hub down onto the pegs, right on top of the motors."
5  | MiningDrillTruck/05-front-carrier | renders/step-005.png | 2x peg, 1x 5x7 frame | 55 225 | yes | "Pin a 5x7 frame onto the Hub's front face, up off the floor -- that's the front axle shelf."
6  | MiningDrillTruck/06-front-axle    | renders/step-006.png | 1x 11-module axle | 55 225 | yes | "Slide an axle through the frame."
7  | MiningDrillTruck/07-front-wheels  | renders/step-007.png | 2x wheel | 55 225 | yes | "Push a wheel onto each end -- 4 wheels now!"
8  | MiningDrillTruck/08-drill-beam    | renders/step-008.png | 1x 7M beam, 2x peg | 55 225 | yes | "Pin a beam across the front of the frame, just above the axle."
9  | MiningDrillTruck/09-drill-motor   | renders/step-009.png | 2x peg, 1x Small Angular Motor | 55 225 | yes | "Pin the drill motor onto that beam, disc facing out."
10 | MiningDrillTruck/10-drill-axle    | renders/step-010.png | 1x 8M axle | 45 180 | yes | "Push a long axle into the disc."
11 | MiningDrillTruck/11-drill-bit     | renders/step-011.png | 3x nose cone, 1x bush | 45 180 | yes | "Stack the pointy cones on the axle and lock them with a bush."
12 | MiningDrillTruck/12-top-rails     | renders/step-012.png | 2x 15M beam, 4x peg | 45 250 | yes | "Pin a long rail onto each side of the Hub, on the row below the very top."
13 | MiningDrillTruck/13-bottom-rails  | renders/step-013.png | 2x 15M beam, 4x peg | 45 250 | yes | "Pin a second rail on each side, one row down, so the pair cannot fold."
14 | MiningDrillTruck/14-uprights      | renders/step-014.png | 2x 3M beam, 4x 3M peg | 40 250 | yes | "Stand a short beam up at the far end of each rail pair."
15 | MiningDrillTruck/15-sensor        | renders/step-015.png | 2x 3M peg, 1x Distance Sensor | 40 250 | yes | "Pin the sensor onto both uprights, eyes looking ahead."
16 | MiningDrillTruck/16-deck-pegs     | renders/step-016.png | 4x peg | 70 225 | yes | "Stand 4 pegs up on the Hub's top."
17 | MiningDrillTruck/17-decks         | renders/step-017.png | 2x plate w. holes | 70 225 | yes | "Press a plate onto the front pegs and one onto the back pegs."
18 | MiningDrillTruck/18-seat          | renders/step-018.png | 1x seat | 55 225 | yes | "Add a seat up on the front deck."
19 | MiningDrillTruck/19-dish          | renders/step-019.png | 1x round dish | 55 45 | yes | "Press the clear dish down onto a rear-deck stud."
20 | MiningDrillTruck/20-driver        | renders/step-020.png | minifig parts | 55 225 | yes | "Build the driver and sit them in the seat, facing the drill."
21 | MiningDrillTruck/21-eyes          | renders/step-021.png | 2x round tile | 35 180 | yes | "Give the truck two eyes on the front frame."
22 | MiningDrillTruck/22-antennae      | renders/step-022.png | 2x whip/aerial | 55 45 | yes | "Add wiggly antennae on the rear deck, beside the dish."
23 | MiningDrillTruck/23-sidekick      | renders/step-023.png | 1x dog | 55 45 | yes | "Tuck in a riding buddy on the back deck."
24 | MiningDrillTruck/24-code          | TBD (no render -- coding page) | (none) | - | no | "Now let's teach Digger to dig!"
```
