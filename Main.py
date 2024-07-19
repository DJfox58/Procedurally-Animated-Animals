import pgzrun
from pgzhelper import *
import pgzero.screen
screen : pgzero.screen.Screen

WIDTH  = 1280
HEIGHT = 1024

nodeArray = []

angles = [0,0]
class NodeGroup:
    def __init__(self, speed, headSize, headConstraintRadius, startingPosition):
        self.speed = speed
        self.desiredPoint = [0,0]
        self.startingPosition = startingPosition
        self.headNode = Node(None, None, headConstraintRadius, headSize, startingPosition)
        self.totalNodes = 1


    def attachNewNode(self, constraintRadius, size):
        curNode = self.headNode

        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()

        curNode.setNextNode(Node(None, curNode, constraintRadius, size, [self.startingPosition[0]-40*self.totalNodes, self.startingPosition[1]]))
        self.totalNodes += 1

        

    def drawSegments(self):
        curNode = self.headNode
        screen.draw.circle(curNode.position, curNode.size, (200,0,0))
        screen.draw.circle(curNode.getPointOnNodeRelativeToPrevious(90), 3, (0, 0, 200))
        screen.draw.circle(curNode.getPointOnNodeRelativeToPrevious(-90), 3, (0, 0, 200))

        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()
            screen.draw.circle(curNode.position, curNode.size, (200,0,0))
            screen.draw.circle(curNode.getPointOnNodeRelativeToPrevious(90), 3, (0, 0, 200))
            screen.draw.circle(curNode.getPointOnNodeRelativeToPrevious(-90), 3, (0, 0, 200))


    def updateHeadNode(self):
        self.headNode.desiredPoint = self.desiredPoint

    def updateNodePositions(self):
        vectorToDesiredPos = [self.desiredPoint[0] - self.headNode.position[0], self.desiredPoint[1] - self.headNode.position[1]]
        vectorToDesiredPos = normalizeVector(vectorToDesiredPos)
        vectorToDesiredPos = multiplyVectorByScalar(vectorToDesiredPos, self.speed)
        self.headNode.position[0] += vectorToDesiredPos[0]
        self.headNode.position[1] += vectorToDesiredPos[1]

        curNode = self.headNode

        while curNode.getNextNode() != None:
            curNode = curNode.getNextNode()
            curNode.updateNodePosition()

            prevNodeAngle = math.degrees(curNode.getPreviousNode().calculateAngleToConnectedNode())
            curNodeAngle = math.degrees(curNode.calculateAngleToConnectedNode())
            if prevNodeAngle > 180:
                prevNodeAngle = prevNodeAngle - 360
            if curNodeAngle > 180:
                curNodeAngle = curNodeAngle - 360   

            angleDifference = (curNodeAngle - prevNodeAngle)
            if 270 > abs(angleDifference) > 90:
                newPos1 = curNode.getPreviousNode().getPointOnNodeConstraintRadiusRelativeToPrevious(90)
                newPos2 = curNode.getPreviousNode().getPointOnNodeConstraintRadiusRelativeToPrevious(-90)
                
                #Because 2 possible vectors exist that form the desired angle, we create both then check with is closer to the node's current vector
                #This finds the correction that is closest to the nodes current position and creates the most natural look
                angleDiff1 = calculateAngleBetweenVectors(curNode.calculateVectorToConnectedNode(), getVectorFromPoints(newPos1, curNode.previousNode.position))
                angleDiff2 = calculateAngleBetweenVectors(curNode.calculateVectorToConnectedNode(), getVectorFromPoints(newPos2, curNode.previousNode.position))
                angles[0] = math.degrees(angleDiff1)
                angles[1] = math.degrees(angleDiff2)
                if angleDiff1 < angleDiff2:
                    curNode.position = newPos1
                    #print("cw")
                else:
                    curNode.position = newPos2
                    #print("ccw")
                
                
    
        








class Node:
    def __init__(self, nextNode, previousNode, constraintRadius, size, position, desiredPoint=None):
        self.nextNode = nextNode
        self.previousNode = previousNode
        self.constraintRadius = constraintRadius
        self.size = size
        self.position = position


    def updateNodePosition(self):
        curVector = self.calculateVectorToConnectedNode()
        normalizedVector = normalizeVector(curVector)
        correctedVector = multiplyVectorByScalar(normalizedVector, self.constraintRadius)
        self.position = [self.previousNode.position[0] - correctedVector[0], self.previousNode.position[1] - correctedVector[1]]


    def calculateVectorToConnectedNode(self):
        connectedNodePosition = self.previousNode.position
        xDisp = connectedNodePosition[0] - self.position[0]
        yDisp = connectedNodePosition[1] - self.position[1]
        return [xDisp, yDisp]


    def calculateAngleToConnectedNode(self):
        normalizedVector = [0, 0]
        if self.previousNode == None:
            normalizedVector = normalizeVector([self.desiredPoint[0] - self.position[0], self.desiredPoint[1] - self.position[1]])
        else:
            normalizedVector = normalizeVector(self.calculateVectorToConnectedNode())
        angle = math.acos(normalizedVector[0])
        if normalizedVector[1] < 0:
            angle = 2*math.pi - angle
        return abs(2*math.pi - angle)
    

    
    #Returns a point on a node circle relative to the angle of the vector from it to the previous node
    def getPointOnNodeRelativeToPrevious(self, angleDeg):
        initialAngle = self.calculateAngleToConnectedNode()
        offset = math.radians(angleDeg)
        newAngle = initialAngle + offset
        posVector = [self.size*math.cos(newAngle), -self.size*math.sin(newAngle)]
        return [self.position[0] + posVector[0], self.position[1] + posVector[1]]


    def getPointOnNodeConstraintRadiusRelativeToPrevious(self, angleDeg):
        initialAngle = self.calculateAngleToConnectedNode()
        offset = math.radians(angleDeg)
        newAngle = initialAngle + offset
        posVector = [self.constraintRadius*math.cos(newAngle), -self.constraintRadius*math.sin(newAngle)]
        return [self.position[0] + posVector[0], self.position[1] + posVector[1]]


    def getPreviousNode(self):
        return self.previousNode
    
    def getNextNode(self):
        return self.nextNode
    
    def setNextNode(self, nextNode):
        self.nextNode = nextNode



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




def calculateAngleBetweenVectors(v1, v2):
    return math.acos(vectorDotProduct(v1,v2)/(calculateVectorMagnitude(v1)*calculateVectorMagnitude(v2)))




nodeGroup = NodeGroup(5, 30, 25, [400, 400])
nodeGroup.attachNewNode(30, 30)
nodeGroup.attachNewNode(30, 25)

for i in range(20):
    nodeGroup.attachNewNode(30, 28 - i)



def update():
    screen.clear()
    nodeGroup.updateHeadNode()
    nodeGroup.updateNodePositions()
    #print(math.degrees(nodeGroup.headNode.getNextNode().calculateAngleToConnectedNode()))

    headVector = nodeGroup.headNode.getPointOnNodeRelativeToPrevious(0)
    headVector[0] -= nodeGroup.headNode.position[0]
    headVector[1] -= nodeGroup.headNode.position[1]
    headVector = normalizeVector(headVector)
    #print(headVector)

def on_mouse_move(pos):
    nodeGroup.desiredPoint = pos

def draw():
    screen.fill((255, 255, 255))
    nodeGroup.drawSegments()

    if angles[0] < angles[1]:
        screen.draw.text("cw " + str(angles[0]), [50, 150], color='green')
        screen.draw.text(" ccw " + str(angles[1]), [150, 50], color="red")
    elif angles[0] > angles[1]:
        screen.draw.text("cw " + str(angles[0]), [50, 150], color='red')
        screen.draw.text(" ccw " + str(angles[1]), [150, 50], color="green")

    

pgzrun.go()




#


