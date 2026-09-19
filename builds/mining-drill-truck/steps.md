# Steps -- Mining Drill Truck

Human connection language. Numbers **must** match `0 STEP` in `model.ldr`
(LeoCAD step 1 = first `0 STEP`). Template: `context/connection-language.md`.

Step 1 -- rear motors
  Sub: drive
  Bin: Prime
  Add: 2x White Large Motor | kit 45678
  Do: Stand the two Large Motors on end, side by side, output discs facing
      out to the sides (left motor's disc points left, right motor's disc
      points right). This is skid steer -- each motor drives its own rear
      wheel directly, no shared axle.
  Check: The two motors sit flush against each other in the middle, discs
      facing opposite ways, both at the same height.

Step 2 -- rear axles and wheels
  Sub: drive
  Bin: Prime
  Add: 2x Bright Yellow 3M cross axle | kit 45678
       2x Multicombination WHEEL DIA.56 | kit 45678
  Do: Push a short 3M axle into each motor's output disc, then push a wheel
      onto the end of each axle.
  Check: Hand-turn a wheel -- the matching motor's disc turns with it, and
      the other motor doesn't move.

Step 3 -- tie the Hub to the motors
  Sub: base
  Bin: Prime
  Add: 6x Black connector peg (friction) | kit 45678
  Do: Stand a peg up in the 6 pin-holes across the tops of the two motors
      that sit toward the back and the middle (3 per motor). Leave the
      front-most pair empty -- those get in the way of the sensor rails
      later.
  Check: 6 pegs stand up evenly, 3 on each motor, with a gap at the front
      of each motor top.

Step 4 -- Hub
  Sub: base
  Bin: Prime
  Add: 1x Bright Yellow SPIKE Prime Hub | kit 45678
  Do: Lower the Hub straight down onto the 6 pegs so its bottom face lands
      flush on the motor tops, motors hidden underneath.
  Check: The Hub sits level and doesn't rock. Peek underneath -- both motor
      discs and wheels are still free to spin.

Step 5 -- front axle carrier
  Sub: base
  Bin: Prime
  Add: 2x Black connector peg (friction) | kit 45678
       1x Black BEAM FRAME 5X7 | kit 45678
  Do: Push a peg into each of the two pin-holes on the Hub's front face
      (the short wall, toward the drill). Hang the 5x7 frame on those pegs
      so it stands up like a shield on the front of the Hub, shifted up one
      so the bottom of the frame is above the floor. The frame's side holes
      still run left-to-right at the same height as the rear axle.
  Check: The frame sits flush on the Hub's front, doesn't wobble, doesn't
      scrape the table, and you can see a hole going through from left to
      right at wheel height.

Step 6 -- front axle
  Sub: base
  Bin: Prime
  Add: 1x Bright Yellow 11-module cross axle | kit 45678
  Do: Slide the long axle through the side-hole of the 5x7 frame that sits
      at wheel height (two holes down from the top of the frame) so it
      sticks out evenly on both sides.
  Check: The axle spins freely and sticks out the same amount on each side.

Step 7 -- front wheels
  Sub: base
  Bin: Prime
  Add: 2x Multicombination WHEEL DIA.56 | kit 45678
  Do: Push a wheel onto each end of the front axle, matching the same width
      as the rear wheels.
  Check: All 4 wheels now spin freely and the front pair doesn't touch the
      rear pair.

Step 8 -- drill-motor beam
  Sub: drill
  Bin: Prime
  Add: 1x Medium Azur 7M beam | kit 45678
       2x Black connector peg (friction) | kit 45678
  Do: Pin the 7M beam across the front of the 5x7 frame (two pegs through
      the frame into the beam), so it sits just above the front axle.
  Check: The beam is level and doesn't wobble. You can still spin the
      front axle by hand.

Step 9 -- drill motor
  Sub: drill
  Bin: Prime + Essential
  Add: 2x Black connector peg (friction) | kit 45678
       1x White Small Angular Motor | kit 45345
  Do: Pin the Small Angular Motor onto that beam, output disc facing
      forward, so the whole motor sits in front of the axle -- not on it.
      Port C.
  Check: The disc faces straight out the front. Turning the disc by
      hand doesn't rub on the frame or the wheels.

Step 10 -- drill axle
  Sub: drill
  Bin: Essential
  Add: 1x Black 8M cross axle | kit 45345
  Do: Push the 8M axle into the motor's output disc (a longer axle than
      you'd guess -- three cones need the extra length).
  Check: The axle sticks straight out the front and turns with the disc.

Step 11 -- drill bit
  Sub: drill
  Bin: Essential
  Add: 3x Bright Orange nose cone (2x2x2) | kit 45345
       1x Bright Red bush | kit 45345
  Do: Stack the 3 nose cones on the axle, points facing away from the
      motor, nested snugly against each other. Push the red bush on last,
      right over the very point of the drill, so the cones can't slide off.
  Check: Hand-turn the motor -- the whole cone stack spins with the disc,
      no wobble, no gap between the first cone and the disc. The bush is
      the wide one, and it should cover the drill's point rather than sit
      behind it.

Step 12 -- top sensor rails
  Sub: sensor
  Bin: Prime
  Add: 2x Black 15M beam | kit 45678
       4x Black connector peg (friction) | kit 45678
  Do: Pin a 15M beam onto each side of the Hub, sticking forward from
      the side pin-holes on the row one below the Hub's very top -- two
      pegs per beam, at the row's near and far holes, so no single beam
      can swing.
  Check: Both rails sit at the same height, clear of the front wheels,
      and don't fold down when you tug the far end.

Step 13 -- bottom sensor rails
  Sub: sensor
  Bin: Prime
  Add: 2x Black 15M beam | kit 45678
       4x Black connector peg (friction) | kit 45678
  Do: Pin a second 15M beam onto each side, one row below the first,
      same two-peg pattern. The two beams on a side must run on two
      different lines, not stacked on the same one (that would let the
      whole gantry hinge down even though each beam is pinned solid on
      its own).
  Check: There is a visible gap between each rail and the front wheel.
      Tug -- neither pair of rails should fold.

Step 14 -- sensor uprights
  Sub: sensor
  Bin: Prime
  Add: 2x Bright Yellow 3M beam | kit 45678
       4x Bright Blue connector peg 3M (friction) | kit 45678
  Do: At the far end of the rails, stand a short 3M beam upright on
      each side. A long peg through the top rail catches the upright's
      top; a long peg through the bottom rail (a little further out)
      catches the upright's middle. Two rows, so the uprights cannot
      swing.
  Check: Both uprights stand straight and don't wiggle.

Step 15 -- distance sensor
  Sub: sensor
  Bin: Prime
  Add: 2x Bright Blue connector peg 3M (friction) | kit 45678
       1x White Distance Sensor | kit 45678
  Do: Pin the Distance Sensor into both uprights, eyes facing forward.
      A last long peg through the bottom of each upright and the sensor
      locks that end down too.
  Check: The sensor's eyes point out the front, above the wheel bottoms,
      and don't touch the spinning cones. Tug the sensor -- it should
      not fold down.

Step 16 -- cab deck pins
  Sub: cab
  Bin: Prime
  Add: 4x Black connector peg (friction) | kit 45678
  Do: Stand a peg up in each of the Hub's 4 top pin-holes (2 toward the
      front, 2 toward the back), so half of each peg sticks up above the
      Hub's top face.
  Check: 4 pegs stand up evenly, 2 near the front edge and 2 near the back
      edge of the Hub's top.

Step 17 -- cab decks
  Sub: cab
  Bin: Prime
  Add: 2x Black PLATE 2X8 W. HOLES | kit 45678
  Do: Press one plate down onto the 2 front pegs and the other plate down
      onto the 2 back pegs, holes lined up over the pegs. These plates give
      you studs to build on, right on top of the smooth Hub.
  Check: Both plates sit flat and don't wiggle -- the front one is where the
      driver sits, the back one is where the dog rides.

Step 18 -- seat
  Sub: cab
  Bin: Essential
  Add: 1x Bright Red SEAT 2X2X2 | kit 45345
  Do: Press the seat onto the front deck, facing forward, toward the drill.
  Check: The seat is level and faces forward, up on the deck, not down on
      the Hub.

Step 19 -- radar dish
  Sub: cab
  Bin: Essential
  Add: 1x Transparent Light Blue round plate (D32) | kit 45345
  Do: Press the round clear plate down onto a stud on the rear deck, flat,
      like a radar dish. (Standing it on its edge cannot snap to anything.)
  Check: The dish sits on a stud and doesn't slide off.

Step 20 -- driver
  Sub: cab
  Bin: Prime
  Add: 1x Black mini lower part | kit 45678
       1x Light Royal Blue mini upper part | kit 45678
       1x Bright Yellow mini head | kit 45678
       1x Black mini wig | kit 45678
  Do: Snap the driver minifig together (legs, torso, head, hair) and sit
      them in the seat on the front deck, facing the drill.
  Check: The driver sits in the seat facing forward, up on the deck, above
      the Hub. (The 3D preview shows them standing beside the seat --
      minifig clutch isn't in the CAD. Sit them at the table.)
  Note: the specific printed head isn't in the free LDraw part library, so
      the 3D preview shows a plain block for it -- use the real head at the
      table.

Step 21 -- eyes
  Sub: face
  Bin: Prime
  Add: 2x Black 1x1 round tile | kit 45678
  Do: Press one round tile on each side of the 5x7 frame's front face,
      above the drill motor, like two eyes.
  Check: The two "eyes" are level with each other and centered above the
      drill.

Step 22 -- antennae
  Sub: face
  Bin: Essential
  Add: 2x White whip/aerial | kit 45345
  Do: Push one antenna into each end stud of the rear cab deck, so they
      stick up behind the driver, beside the radar dish.
  Check: Antennae wiggle when you tap them.

Step 23 -- sidekick
  Sub: face
  Bin: Essential
  Add: 1x Medium Nougat dog | kit 45345
  Do: Set the dog on the back deck, riding behind the driver.
  Check: Does Digger look like it's smiling? Good -- that's the point.
  Note: the dog mold isn't in the free LDraw part library, so the 3D
      preview shows a plain block for it -- use the real dog piece at the
      table.

Step 24 -- program
  Sub: code
  Bin: (SPIKE App -- no new bricks)
  Add: (none)
  Do: Open the SPIKE App, connect to the Prime hub, and build the program
      in `code.md`.
  Check: See `code.md` "Success."
