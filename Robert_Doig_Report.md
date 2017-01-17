# Dugeon Maker

##Aims 
To create a procedurally generated level using a dungeon tool kit.


## Description

This project focuses on the level that we had imagined creating. At the beggining we had wanted to create a combination of large rooms and connecting hallways. However after some thought of the type of level we wanted to create, a different approach was adopted. We divided the project into two main chambers. Stairways and rooms. This allows us to create interesting levels in the theme of Hogwarts from the Harry Potter series.


## Technical Design 

When we had the idea of what we wanted the project to output we divided up the tasks into three main areas, stairs, rooms and artist input or world generation. After this was defined a project flow diagram and basic structure was created. Esentially we would handle a part of the process and pass the output on to the next person in the chain.

This diagram shows the basic structure of how the data passed through the system 
========================== Diagram link to flow diagram ===========================================


The tasks were divided up as follows: 
  - Witek to handle the artist input and overview of the level 
  - Louis to create rooms with interesting pillars and features 
  - Robert to implement the stairway generator to connect doors on mutliple levels. 
  - Henry to create a web interface and run the tool on a server for users to control

## Stairs Overview 

For my section of the task I approached the creation of the stairways with a completely random connection of meshes. However after more consideration a more sophisticated implementation was needed so that a path was always created between the different doors. The A* path finding algorithm was choosen because of it tile based design. The 2D implementation discussed in Sebastian Lague tutorial on Youtube ( [Link to Tutorial](https://www.youtube.com/watch?v=-L-WgKMFuhE&t=581s) )  was the psuedo code used to create the 3D version of the algorithm. This approach was not easily converted to 3D and will be discussed in more detail in the explaination below. 




## A* path finding 3D Explaination
