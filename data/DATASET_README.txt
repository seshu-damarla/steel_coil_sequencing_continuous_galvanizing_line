*** Data accompanying the research on CGL Scheduling Problem ***
Author: Alvarez-Gil, N. (Nicolás) (uo226901@uniovi.es)
Business Management Department, Polytechnic School of Engineering of Gijón, University of Oviedo


*** Dataset description ***
This dataset contains the cost matrix of several instances of the scheduling problem of a Continuous Galvanizing Line (CGL). They are real instances of a CGL of a 
Spanish steel company, in which a fixed group of steel coils should be sequenced. The cost of sequencing two coils together can be:

 - A cost (c[i,j] != -1): in this case it is possible to produce coil i right before coil j, and the value c[i,j] represents the actual production cost.
 - A constraint (c[i,j] = -1): in this case coil i cannot be produced right before coil j because of technical limitations of the line (coil i cannot link directly to coil j, but
   it can be produced at any other positions before coil j).


The problem consists in finding a minimum-cost Hamiltonian path: a minimum-cost sequence that contains all the nodes just once.
The main challenge is to find a feasible sequence: a sequence without constraints.
The costs are asymmetric: cost[i,j] != cost[j,i]

The name of the instances follows the notation cgl_X:
  X = the size of the instances(the total number of coils to be sequenced)

ALL the instances are known to be sequenceable: it exist a Hamiltonian path (*)
  
The challenge is to find an algorithm able to provide minimum-cost feasible solutions for all the instances.
 

 
 
*** Example ***

The instance "cgl_17.txt" contains the following matrix:

-1;300;-1;654;926;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1
305;-1;963;117;237;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1
952;493;-1;704;686;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1
678;123;-1;-1;41;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1
946;237;1155;34;-1;804;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1;-1
-1;-1;-1;-1;-1;-1;71;1721;-1;-1;-1;-1;-1;-1;-1;-1;-1
-1;-1;-1;-1;-1;73;-1;1777;-1;-1;-1;-1;-1;-1;-1;-1;-1
-1;-1;-1;-1;-1;2034;2020;-1;634;634;634;634;634;634;634;634;67
-1;-1;-1;-1;-1;-1;-1;685;-1;0;0;0;0;0;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;-1;0;0;0;0;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;-1;0;0;0;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;0;-1;0;0;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;0;0;-1;0;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;0;0;0;-1;0;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;0;0;0;0;-1;0;308
-1;-1;-1;-1;-1;-1;-1;685;0;0;0;0;0;0;0;-1;308
-1;-1;-1;-1;-1;-1;-1;77;293;293;293;293;293;293;293;293;-1


The size of the instance is equal to the size of the square matrix, and the solution must be a sequence of the same size with each node appearing
just once. 

The element (i,j) of the matrix represent the cost of processing coil i right before coil j.

From Row 1:
[0, 0]:   (Coil 0 -> Coil 0) = -1 (not possible, each coil must appear just once in the sequence)
[0, 1]:   (Coil 0 -> Coil 1) = 300 (cost of producing coil 0 right before coil 1)
[0, 2]:   (Coil 0 -> Coil 2) = -1 (not possible, technical constraint)
[0, 3]:   (Coil 0 -> Coil 3) = 654 (cost of producing coil 0 right before coil 3)
[0, 4]:   (Coil 0 -> Coil 4) = 926 (cost of producing coil 0 right before coil 4)
(...)

From Row 2:
[1, 0]:   (Coil 1 -> Coil 0) = 305 (cost of producing coil 1 right before coil 0)
[1, 1]:   (Coil 1 -> Coil 1) = -1 (not possible, each coil must appear just once in the sequence)
[1, 2]:   (Coil 1 -> Coil 2) = 963 (cost of producing coil 1 right before coil 2)
[1, 3]:   (Coil 1 -> Coil 3) = 117 (cost of producing coil 1 right before coil 3)
[1, 4]:   (Coil 1 -> Coil 4) = 237 (cost of producing coil 1 right before coil 4)
(...)


A possible solution for this instance is:
Seq = [2, 0, 1, 3, 4, 5, 6, 7, 16, 11, 15, 10, 8, 12, 14, 13, 9]
Cost = 952 + 300 + 117 + 41 + 804 + 71 + 1777 + 67 + 293 + 0 + 0 + 0 + 0 + 0 + 0 + 0 =  4422




*** Additional Comment ***

 (*) For all the instances, the sequence [0, 1, 2, 3, 4, 5, ..., n-1] (being n the size of the instance) is a feasible sequence, but the 
algorithm should be able to find a minimun-cost feasible sequence without using this information.
