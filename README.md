# Billiard Ball Computing

Billiard ball computing is a reversible form of computing that depends upon elastic collisions between "billiard" balls and mirrors that are able to reflect the balls. These interactions can be used to simulate logic gates and provide a Turing Complete form of computation as proved by Edward Fredkin and Tommaso Toffoli during their research on conservative logic gates.

[Learn more about Billiard Ball Computers](https://en.wikipedia.org/wiki/Billiard-ball_computer)

## Example: Billiard Ball Full Adder

<img width="944" height="831" alt="image" src="https://github.com/user-attachments/assets/83043dd3-d502-468c-b5c5-90d3901721e4" />

### IO Key
- Red ball — A
- Green ball — B
- Black ball — Cin
- Purple Square — Sum
- Cyan Square — Cout

## Background

This project was originally designed as an assignment for the University of Notre Dame's course [CSE 40932 - Exotic Computing](https://www.coursicle.com/nd/courses/CSE/40932/).

The original scope was limited to the Full Adder, designed as a brief demonstration of the power of reversible computing and specifically the Billiard Ball Model.

We want to take the basic physics engine and framework for the Full Adder simulation and turn it into something far more robust and versatile.

## Goals

To do this, our current goals are to:

- Create a UI that allows for dynamic adding and removal of balls and mirrors, configuring orientation of mirrors and direction of balls, configuring grid size, and controlling the speed of the simulation.
- Create a way to download your own creations and import creations from others into the simulator.

## Vision

The vision is to create software for Billiard Ball Computing that will provide students and people interested in reversible computing a way to see and explore the concepts visually. Further, we want to create a community around Billiard Ball Computing similar to the Minecraft Redstone Computing community where people can design and then share their creations with others. For this reason we will be releasing this software under an open source license to both push forward the development of the simulator and give any one the chance to contribute to it.

## Current Features
- Added dynamic UI for adding and removing balls, mirrors, inputs, and outputs.
- Separate Simulation and Edit modes
- Ability to change grid size
- Load and save designs using JSON format

## Simulation Controls
- Press space to start simulation
- Press r to reverse balls in motion
- Output squares will stop balls from moving once reached

## To be Added
- Color controls for each object
- More visually appealing UI

