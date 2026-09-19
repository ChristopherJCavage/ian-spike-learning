# Pre-flight -- Rainforest Drop Zone

`ldrcheck` proves static geometry and clutch. On this build that is a smaller
claim than usual: there is no mechanism here, so almost everything that can
go wrong is either a piece that will not actually clutch, or a piece standing
where the drone needs to fly. Run the machine checks, then do the table
checks with the drone in your hand.

## Machine (must be green)

```
python3 tools/ldrcheck.py check builds/rainforest-drop-zone/model.ldr
python3 tools/ldrcheck.py steps builds/rainforest-drop-zone/model.ldr
python3 tools/ldrcheck.py fixtures
python3 tools/pages.py check builds/rainforest-drop-zone
```

Expected:

- model: 17 parts, 9 steps, 0 problems, and no NO GEOMETRY section at all
  (that section only prints when something is missing);
- build order: 0 problems;
- pages: 10 instruction blocks and rows, 9 step PNGs, 0 problems;
- fixtures pass.

There is no `blocks.py` line. This build has no program of its own -- the
program lives with the drone, in `builds/seed-drone/program.spike`, and it is
this island's red band that it watches for.

The model declares:

```
0 !LDRCHECK GROUND 8
0 !LDRCHECK FRONT +Z
0 !LDRCHECK JOINS 87079.dat 92438.dat
0 !LDRCHECK FACES 73200b.dat +Z
0 !LDRCHECK GRIP 30089.dat 76382.dat
```

`GROUND 8` is the table: the plate's own underside. `JOINS` says the red
drop-zone tiles really are clutched to the plate rather than resting on it.
`FACES` keeps the ranger looking down the lane. `GRIP` says the camera in her
hand is meant to share volume with the hand, and fails if it ever stops
touching her.

## Table checks

### 1. Read the drop zone with the sensor

This is the check that decides whether the model works, so do it first.

Hold the drone's Colour Sensor over the red band at the height it will really
pass -- about 1 to 2 cm. Watch the Hub, not the tiles. You want a steady
**red** over the band, and nothing over the white plate either side of it.

Do this before class, under the room lights that will actually be on. Colour
sensing is the one thing in this repo that a render cannot even hint at.

If it flickers, you are too high or too low, not too fast. There is no orange
anywhere near the target in this version, so red-versus-orange -- the main
sensor risk in the earlier 16x16 island -- cannot happen here.

**The seed is red too**, because Bright Red is the only ball colour in the
box. A dropped seed lying on the white plate is a valid target as far as the
sensor is concerned, so flying back over one will fire the program again.
Pick the seed up between passes. Not a real limitation, but it will look like
a bug the first time it happens.

### 2. Fly the drone down the lane at height

Hold the Seed Drone level and walk it down the lane at the height you will
actually fly it, in both directions. Nothing may catch the rotor blades or
the tray.

The two bushes are the tallest things here at about 5.6 cm. The blades sweep
about 58 LDU -- just over 2 cm -- above the treetops, which is nearly twice
the margin the two-brick trunks left in the earlier version. Check that
clearance with the tray **loaded**: the seed sits above the tray floor and
the drone rides lower when you are holding it carefully.

Also check the drone's own width against the walls. The walls are only 1 cm
tall, so the body passes over them easily, but the skids must not clip them
if the drone dips.

### 3. Sight along the lane

Crouch to table height and look down the lane from each end. You should see
red tile, white plate and green wall, and nothing else in the lane. If a
grass tuft has crept over the edge of the red, move it: from above the sensor
cannot tell a green stem from a green plate.

Then look straight down and check the two red tiles are actually butted
together and reach both walls. A one-stud gap between them puts a white
stripe through the target, and the sensor will read that stripe. There should
be no white at all inside the lane -- if there is, a tile is one stud out.

### 4. Push on everything decorative

The trees, the grass, the frog and the ranger are all annotated
`role: decorative`, which means `ldrcheck` never asked whether any of them
clutches anything. Press each one down and then try to nudge it sideways:

- each bush should grip all four studs of its trunk;
- each trunk should not twist on the plate;
- each grass tube should be centred on one stud, flat down -- if it rocks,
  it is bridging two studs;
- both of the ranger's feet should be on studs.

This is the one check on this build that cannot be automated at all, and it
is why the model's header comment lists the stud parity for each of these
parts by hand.

### 5. Check the ranger stays standing

Nudge the table. The figure is the only tall, narrow thing on the island, and
a figure holding an item out in front is easy to topple. If she falls
repeatedly, move her one stud row further from the tree so the canopy is not
brushing her.

## What the checker cannot see

- **Whether anything decorative actually clutches.** See table check 4. Six
  of the seventeen parts here are decorative, so this is a third of the model.
- **Whether the two red tiles are flush.** `JOINS` proves each tile is
  clutched to the plate. It says nothing about whether they touch each other,
  and a gap between them is a white stripe through the target.
- **Whether the sensor can read red at flying height.** See table check 1.
- **Colour.** `COLOUR vs KIT` proves each part exists in that colour in the
  box. It cannot tell you the island looks like rainforest, and an early
  version of this model passed every check while looking like a running track
  with lanes. Look at the render.
- **How long it takes to build.** Nine steps and twenty parts is the whole
  reason this version exists, and no check enforces it. If a step gets added
  back, ask what it is worth against the minute it costs.
