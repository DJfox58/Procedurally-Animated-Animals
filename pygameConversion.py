#This file uses a procedural animation technique to simulate a snake slithering around the screen
#The technique employs constrained circles and draws a snake outline around the sides of the nodes




import math
import pygame
import pygame.gfxdraw

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake:)")

run = True







#Each node group is comprised of at least 1 head node and any subsequent body nodes. The final node is considered the tail node and can have draw points added to it
#to create more detailed polygon draws
class NodeGroup:
    """
    A grouped set of nodes that comprise the spine of a simulated animal
    Each node group is comprised of at least 1 head node and any subsequent body nodes. The final node is considered the tail node and can have draw points added to it
    to create more detailed polygon draws.
    """
    def __init__(self, speed, headSize, headConstraintRadius, startingPosition, extraDrawAngles=None):
        """Constructor only creates head node. Additional nodes must be added using the attachNewNode() method

        Args:
            speed (_float_): the speed of the snake. 1 is slow, 5 is fast
            headSize (_type_): the size of the initial head node
            headConstraintRadius (_type_): the radius around the head node that the next node in the group is constrained to
            startingPosition (_[int, int]_): the starting position of the head
            extraDrawAngles (_[int, int...]_, optional): _description_. Any extra points to draw the animal polygon on the head. 0 is the front of the head, +ve angles are the left side of the head, & -ve angles are the right side of the head. Defaults to None.
        """

        
        self.speed = speed
        
        
        self.desiredPoint = [0,0]
        """The point the snake will move towards
        """
        self.startingPosition = startingPosition
        self.headNode = Node(None, None, headConstraintRadius, headSize, startingPosition, [0,0], extraDrawAngles=extraDrawAngles)
        self.totalNodes = 1



    def attachNewNode(self, constraintRadius, size):
        """Attaches a new node to the end of the group

        Args:
            constraintRadius (_int_): constraint radius of the new node
            size (_int_): visual size of the new node
        """
        curNode = self.headNode

        #Finds the current last node in the chain and then connects a new node to it
        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()

        curNode.setNextNode(Node(None, curNode, constraintRadius, size, [self.startingPosition[0]-40*self.totalNodes, self.startingPosition[1]]))
        self.totalNodes += 1


    def attachTailNode(self, constraintRadius, size, pointAnglesList):
        """A special node addition method that is used specifically for the final node in a spine. It has an additional parameter for 
        adding extra draw points to the node for more detail

        Args:
            constraintRadius (_int_): constraint radius of the tails node
            size (_int_): visual size of the new node
            pointAnglesList (_[int, int...]_ (ascending order)): A list of angles relative to the front of the node where the points should be placed. The angles
            must be added in ascending order and must all be POSITIVE
        """
        curNode = self.headNode

        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()

        curNode.setNextNode(Node(None, curNode, constraintRadius, size, [self.startingPosition[0]-40*self.totalNodes, self.startingPosition[1]], extraDrawAngles=pointAnglesList))

        

    def drawSegments(self):
        """Draws the nodes as circles using their sizes as well as points on their left and right sides. 
        This is currently unused as it is not necessary to draw the rendered snake but enabling it 
        can be useful for seeing how the nodes function. The l/r dots are the points that the snake polygon is rendered using

        """
        curNode = self.headNode

        #Main node
        pygame.draw.circle(screen, (200, 200, 200), curNode.position, curNode.size, 5)
        
        #Left dot
        pygame.draw.circle(screen, (0, 200, 0), curNode.leftLink, 3, 5)
        
        #Right dot
        pygame.draw.circle(screen, (0, 0, 200), curNode.rightLink,3, 5)
    
        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()
            pygame.draw.circle(screen, (200, 200, 200), curNode.position, curNode.size, 5)
            pygame.draw.circle(screen, (0, 200, 0), curNode.leftLink, 3, 5)
            pygame.draw.circle(screen, (0, 0, 200), curNode.rightLink, 3, 5)


    def drawEyes(self):
        """Draws the eyes onto the rendered snake. This can be done by finding 2 points on the side of the head
        and scaling them back using vector operations to place them inside the node's radius
        """
        curNode = self.headNode


        normalizedLeftEyeVector = normalizeVector(getVectorFromPoints(curNode.position, curNode.getPointOnNodeRelativeToPrevious(50)))
        leftEyeVector = multiplyVectorByScalar(normalizedLeftEyeVector, curNode.size/2)
        pygame.draw.circle(screen, (255, 255, 255), subtractVectors(curNode.getPointOnNodeRelativeToPrevious(50), leftEyeVector), 10, 0)

        normalizedRightEyeVector = normalizeVector(getVectorFromPoints(curNode.position, curNode.getPointOnNodeRelativeToPrevious(-50)))
        rightEyeVector = multiplyVectorByScalar(normalizedRightEyeVector, curNode.size/2)

        pygame.draw.circle(screen, (255, 255, 255), subtractVectors(curNode.getPointOnNodeRelativeToPrevious(-50), rightEyeVector), 10, 0)
    
    

    
    def connectTheDots(self):
        """Collects all the points tracked on the nodes of the group and creates a polygon around them.
        This creates the shape of the animal and is what is currently used to do rendering.
        """

        #The polygon starts with the rightmost custom point on the head, wraps around all the default left
        #points on the nodes, then does the custom tail points from left to right before going up the 
        #right side default points starting from the tail, ending with the right default point on the head
        headPointList = []
        leftPointList = []
        tailPointList = []
        rightPointList = []

        #The head usually has extra points for a cleaner draw
        curNode = self.headNode
        headPointList = curNode.extraPoints
        
        leftPointList.append(curNode.leftLink)
        rightPointList.append(curNode.rightLink)


        #Adds all the default points of the nodes to the lists
        while curNode.getNextNode() != None:
            leftPointList.append(curNode.leftLink)
            rightPointList.append(curNode.rightLink)
            curNode = curNode.getNextNode()


        #The tail has extra points for a cleaner draw at the end
        tailPointList = curNode.extraPoints

        pointList = []

        #Head points are placed in ascending order (rightmost angles to leftmost angles) therefore
        #they don't have to be reversed before being added to the list
        for point in headPointList:
            pointList.append(point)


        #These go from head to tail and don't need to be reverse
        for point in leftPointList:
            pointList.append(point)

        #Tail points are placed in ascending order, but all must be positive resulting in them being ordered
        #left to right, so the list doesn't need to be reversed
        for point in tailPointList:
            pointList.append(point)

        #Because the right points must be drawn tail to head, we reverse the list 
        rightPointList.reverse()
        for point in rightPointList:
            pointList.append(point)
        

        pygame.draw.polygon(screen, (225, 130, 0), pointList, 0)
        pygame.draw.polygon(screen, (255, 255, 255), pointList, 3)


        #Draws lines on the snake
        #rightPointList.reverse()
        #for i in range(3, self.totalNodes, 3):
            #pygame.draw.line(screen, (0,0,0), leftPointList[i], rightPointList[i], int(10-i*0.03))

            
    def updateHeadNode(self):
        """Updates the point that the head node moves towards
        """
        self.headNode.desiredPoint = self.desiredPoint


    def updateNodePositions(self):
        """Updates the position of each node in the group, and ensures all nodes are within the angle flexibility threshold
        """

        #This block updates the head node's position based on the mouse position
        vectorToDesiredPos = [self.desiredPoint[0] - self.headNode.position[0], self.desiredPoint[1] - self.headNode.position[1]]
        vectorToDesiredPos = normalizeVector(vectorToDesiredPos)
        vectorToDesiredPos = multiplyVectorByScalar(vectorToDesiredPos, self.speed)
        self.headNode.position[0] += vectorToDesiredPos[0]
        self.headNode.position[1] += vectorToDesiredPos[1]
        

        curNode = self.headNode
        curNode.updateDrawPoints()


        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()
            curNode.updateDrawPoints()
            curNode.updateNodePosition()


            #This block aims to ensure that the snake doesn't collapse in on itself, by maintaining a maximum difference in
            #angle between a current node and the previous node it is constrained to

            #We effectively check the difference in angle between the vector connecting the current node to it's previous node and the previous node's
            #vector to it's own constraining node.

            #If the angle is found to be above the threshold, we calculate a new position for the current just within the angle 
            #threshold on the previous node's constraint circle
            prevNodeAngle = math.degrees(curNode.getPreviousNode().calculateAngleToConnectedNode())
            curNodeAngle = math.degrees(curNode.calculateAngleToConnectedNode())
            if prevNodeAngle > 180:
                prevNodeAngle = prevNodeAngle - 360
            if curNodeAngle > 180:
                curNodeAngle = curNodeAngle - 360   

            angleDifference = (curNodeAngle - prevNodeAngle)

            if 340 > abs(angleDifference) > 20:

                #Because 2 possible vectors exist that form the desired angle, we create both then check with is closer to the node's current vector
                #This finds the correction that is closest to the nodes current position and creates the most natural look
                newPos1 = curNode.getPreviousNode().getPointOnNodeConstraintRadiusRelativeToPrevious(160)
                newPos2 = curNode.getPreviousNode().getPointOnNodeConstraintRadiusRelativeToPrevious(-160)

                angleDiff1 = calculateAngleBetweenVectors(curNode.calculateVectorToConnectedNode(), getVectorFromPoints(newPos1, curNode.previousNode.position))
                angleDiff2 = calculateAngleBetweenVectors(curNode.calculateVectorToConnectedNode(), getVectorFromPoints(newPos2, curNode.previousNode.position))
                
                if angleDiff1 < angleDiff2:
                    curNode.position = newPos1
                else:
                    curNode.position = newPos2
                
                
    
        








class Node:
    """The individual nodes that comprise a node group. Each node can be connected to 2 other nodes, one node above it in the chain, 
    and one node below it. Each node can be thought of as a segment of the spine of the creature being simulated, with
    the movement of each node is constrained by the previous node in the group.
    """
    def __init__(self, nextNode, previousNode, constraintRadius, size, position, desiredPoint=None, extraDrawAngles=None):
        self.nextNode = nextNode
        self.previousNode = previousNode
        self.constraintRadius = constraintRadius
        self.size = size
        self.position = position
        self.desiredPoint = desiredPoint
        self.leftLink = self.getPointOnNodeRelativeToPrevious(90)
        self.rightLink = self.getPointOnNodeConstraintRadiusRelativeToPrevious(-90)
        self.extraDrawAngles = extraDrawAngles
        

        #Angles should be provided in ascending order
        self.extraPoints = []

        if extraDrawAngles != None:
            for angle in extraDrawAngles:
                self.extraPoints.append(self.getPointOnNodeRelativeToPrevious(angle))


    def updateNodePosition(self):
        """Updates the node to its new position based on the position of the previous node. Finds the vector between the 
        current and previous nodes then reducing the vector until the current node lies on the constraint circle of the prev node
        """
        curVector = self.calculateVectorToConnectedNode()
        normalizedVector = normalizeVector(curVector)

        #The node is constrained based on the constraintRadius of the previous node
        correctedVector = multiplyVectorByScalar(normalizedVector, self.getPreviousNode().constraintRadius)
        self.position = [self.previousNode.position[0] - correctedVector[0], self.previousNode.position[1] - correctedVector[1]]


    def calculateVectorToConnectedNode(self):
        """Calculates the vector from the current node to the previous node. Note that this vector is not normalized

        Returns:
            _[float, float]_: a [x,y] list representing a 2d vector from the current node to the previous node
        """
        connectedNodePosition = self.previousNode.position
        xDisp = connectedNodePosition[0] - self.position[0]
        yDisp = connectedNodePosition[1] - self.position[1]
        return [xDisp, yDisp]


    def calculateAngleToConnectedNode(self):
        """Calculates the angle to the connected node in radians. right is 0, up is pi/2, left is pi, down is 3pi/2.
        If this is called on a head node (no previous node), then it finds the angle from the head node to the desiredPoint(mouse)

        Returns:
            _float_: the angle from the node to the previous node in radians
        """
        normalizedVector = [0, 0]

        #Head node
        if self.previousNode == None:
            normalizedVector = normalizeVector([self.desiredPoint[0] - self.position[0], self.desiredPoint[1] - self.position[1]])
        #Everything else
        else:
            normalizedVector = normalizeVector(self.calculateVectorToConnectedNode())
        angle = math.acos(normalizedVector[0])
        if normalizedVector[1] < 0:
            angle = 2*math.pi - angle
        return abs(2*math.pi - angle)
    

    
    #Returns a point on a node circle relative to the angle of the vector from it to the previous node
    def getPointOnNodeRelativeToPrevious(self, angleDeg):
        """Returns the screen coordinates of a point on the node's draw circle relative to its front(front is the angle this node makes with the prev node) 
        given an angle. Used to help render the creature by providing points along the nodes to draw a polygon over.
        The similarily named method used for the constraint circle is not used to render the creature, but is useful for debugging

        Args:
            angleDeg (_int_): The angle from the front of the node in degrees

        Returns:
            _[int, int]_: screen coordinates of the requested point on the node's size circle
        """


        initialAngle = self.calculateAngleToConnectedNode()
        offset = math.radians(angleDeg)
        newAngle = initialAngle + offset

        #The y component must be reversed here, as the screen coordinates consider y values up on the screen to be smaller
        #which contradicts the unit circle mindset of x and y coordinates
        posVector = [self.size*math.cos(newAngle), -self.size*math.sin(newAngle)]
        return [self.position[0] + posVector[0], self.position[1] + posVector[1]]


    def getPointOnNodeConstraintRadiusRelativeToPrevious(self, angleDeg):
        """Identical to it's sister method above, other than the fact that the points it finds are on the node's constraint circle

        Args:
            angleDeg (_int_): The angle from the front of the node in degrees

        Returns:
            _[int, int]_: screen coordinates of the requested point on the node's constraint circle
        """
        initialAngle = self.calculateAngleToConnectedNode()
        offset = math.radians(angleDeg)
        newAngle = initialAngle + offset
        posVector = [self.constraintRadius*math.cos(newAngle), -self.constraintRadius*math.sin(newAngle)]
        return [self.position[0] + posVector[0], self.position[1] + posVector[1]]


    def getPreviousNode(self):
        """Returns the previous node this node is connected to

        Returns:
            _Node_:previous nod3
        """
        return self.previousNode
    
    def getNextNode(self):
        """Returns the next node this node is connected to

        Returns:
            _Node_: previous node
        """
        return self.nextNode
    
    def setNextNode(self, nextNode):
        """Sets the next node

        Args:
            nextNode (_Node_): the next node in the chain
        """
        self.nextNode = nextNode

    def updateDrawPoints(self):
        """Updates the points along the node that are used to render the creature
        """
        self.leftLink = self.getPointOnNodeRelativeToPrevious(90)
        self.rightLink = self.getPointOnNodeRelativeToPrevious(-90)

        #If a node (usually the head or tail) has extra points, this block is in charge of updating them 
        if self.extraDrawAngles != None:
            for i in range(len(self.extraDrawAngles)):
                self.extraPoints[i] = self.getPointOnNodeRelativeToPrevious(self.extraDrawAngles[i])
                




###-----------------------------------
#Bunch of vector functions I made that are used throughout the math in the rest of the methods.
#If you want to learn more about the math and formulas behind these functions, take a look at this article
#https://www.superprof.co.uk/resources/academic/maths/analytical-geometry/vectors/vector-formulas.html

def getVectorFromPoints(p1, p2):
    return [p2[0]-p1[0], p2[1]-p1[1]]

def calculateVectorMagnitude(vectorArray):
    return math.sqrt((math.pow(vectorArray[0], 2) + math.pow(vectorArray[1], 2)))

def normalizeVector(vectorArray):
    magnitude = calculateVectorMagnitude(vectorArray)
    normalizedVector = [vectorArray[0]/magnitude, vectorArray[1]/magnitude]
    return normalizedVector


def multiplyVectorByScalar(vectorArray, scalar):
    multipliedVector = [vectorArray[0]*scalar, vectorArray[1]*scalar]
    return multipliedVector


def vectorDotProduct(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]



def subtractVectors(v1, v2):
    return [v1[0]-v2[0], v1[1]-v2[1]]


def calculateAngleBetweenVectors(v1, v2):
    val = 0
    val = vectorDotProduct(v1,v2)/(calculateVectorMagnitude(v1)*calculateVectorMagnitude(v2))
    #In certain scenarios val will be slightly outside of acos domain due to floating point errors. We round val to ensure this
    #doesn't occur
    val = round(val, 8)
    return math.acos(val)
###-----------------------------------    


startingPosition = [400, 400]
specialHeadDrawPoints = [-30, 0, 30]
specialTailDrawPoints = [150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210]
speed = 4

nodeGroup = NodeGroup(speed, 30, 10, startingPosition, specialHeadDrawPoints)

nodeGroup.attachNewNode(10, 30)
nodeGroup.attachNewNode(10, 25)

for i in range(50):
    nodeGroup.attachNewNode(10, 28 - i/3)
    nodeGroup.attachNewNode(10, 28 - i/3)

nodeGroup.attachTailNode(20, 15, specialTailDrawPoints)



clock = pygame.time.Clock()

while run:
    clock.tick(60)
    screen.fill((60,60,60))
    nodeGroup.desiredPoint = pygame.mouse.get_pos()
    nodeGroup.updateHeadNode()
    nodeGroup.updateNodePositions()


    #nodeGroup.drawSegments()
    nodeGroup.connectTheDots()
    nodeGroup.drawEyes()

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
    

    pygame.display.update()

pygame.quit()