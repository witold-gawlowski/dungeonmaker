


Dungeon Generator
-----------------



Louis Bennette
Team: `string team_name;`

Other members:
Rob Doig
Witek Gawlowski



-----------------------------------------------

**Project Overview**

The project aim was to create a randomly generated structure out of tiles. 
My group and I developed a small prototype of a room by using Andy Thomason’s dungeon_generator project on github (https://github.com/andy-thomason/dungeon_generator)

The room was created entirely from the small tile set and we decided that we could make our entire structure using only the small tiles.

We divided our tasks as follows, I worked on building the rooms, Robert worked on building stairwells to connect rooms on different levels and Witek builds the algorithm that calls a room or a stair to be at a certain position with a certain size.

Because we restricted ourselves to using the small tiles only we expanded our tile kit and created new meshes for certain situations.
This is what our final tilekit input looks like:

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/components.png)

As you can see there are a number of different tiles to the original tile kit. Including T and X wall junctions and ceiling and mid wall equivalents. 

**My task:**

I was tasked specifically with the rooms. As I was the first to create an output for the project I also started to create a standard for building rooms. The original plan was to have symetrical and asymmetrical rooms. 

**My implementation**

The rooms are created using a few variables the edges are the connectors between tiles these can be unsatisfied (unconneted to other tiles) or satisfied (connected to other tiles).
The output is a list of node names, their location and their rotation.
The input a both a list of door loactions and a boundary shape inside of which the room can exist. 

The algorithm randomises small shapes within the boundary by cutting up the large shapes into two smaller shapes and repeating the process until the minimum sized shape is reached. Then with this fractured list of shapes only the necessary shapes that connect the doors together are kept. This is then our new random room shape which is then used to place tiles in the correct positions.

As I built my rooms I offloaded the generic functions into a tile_handler class which was responsible for any generic tile manipulation that would otherwise crossover between the stairs and room generation.
The system that was eventually adopted was a create_todo and complete_todo paradigm. When calling create todo the user can specify an edge type to create a todo for. If there are edges of that type that are still not connected to neighbours then the todo gets populated with those edges. The tile name can be specified to only use edges connected to a specific type of tile.

    def create_todo(self, edges, nodes, feature_names = None, tile_name_ = None):

Complete_todo takes an input todo list and checks if a tile can fit at the specified todo locations if it can the tiles are created. The function can take a number of parameters, such as boundaries, limiting where the tiles can be created and masks of areas where tiles can’t be created. Additionally, a specific tile can be created at the todo locations by passing a tile name string. Finally, a fill parameter determines if the function should update the todo for every new tile placed or if the todo should be completed without consideration for newly created edges.

    def complete_todo(self, todo, edges, nodes, boundary = None, mask = None, tile_name = None, flood_fill = False):

Using these two functions I can specify a logical build order for specific tiles at specific locations. I refer to these as my build passes. 
To test the build passes I hand generated shapes and the random room shape was not generated until later on in the project.

My first room was a specified shape and consisted of three build passes, make floor, make walls and make wall corners.

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/dungeonroom0.png)

I then attempted to create a ceiling as well, the ceiling method changed many times during the development and the final output is not exactly what I was hoping for. If I could go back I would have specified a more robust set of tiles to make ceiling generation simpler.

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/dungeonroom1.png)


After the ceilings had been generated I focused on creating a full room. 
I generated pillars, wall mid sections and different height ceilings. 

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/dungeonroom2.png)

Once a full room was created I focused on making randomised rooms work. I developed the algorithm and ran it through my build passes to test the outputs. 

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/dungeonroom3.png)


Additionally, I worked on the conversion steps from Witek’s algorithm for room placement. This was to lower his workload and to start testing how multiple rooms fit together, here is an example output of a small set of interconnected rooms.

![enter image description here](https://raw.githubusercontent.com/witold-gawlowski/dungeonmaker/master/screenshots/dungeonroom5.png)

**Team**

For the project I would say that I’m happy with my team. We got along very well and worked well with each other. We all had a similar expectation and enthusiasm for the project. I would be happy to work with them again.
