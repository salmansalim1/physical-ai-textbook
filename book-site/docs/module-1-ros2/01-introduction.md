---
sidebar_position: 1
---

# Chapter Title
 ROS 2 Fundamentals Introduction to ROS 2
## Introduction

Brief overview of what this chapter covers.

## Key Concepts

### Concept 1
1.1 What is ROS 2?
ROS 2 (Robot Operating System 2) is an open-source framework that helps you build robotic and physical AI systems by providing tools, libraries, and communication standards. Despite its name, ROS is not an operating system like Windows or Linux—it runs on top of Linux and provides middleware for robotics applications.
ROS 2 is used in:
Autonomous vehicles 🚗
Drones 🚁
Industrial robots 🏭
Medical robots 🏥
AI-powered physical systems 🤖
Why ROS exists
Building robots involves:
Sensors (camera, LiDAR, IMU)
Actuators (motors, arms)
AI algorithms (SLAM, navigation)
Real-time communication
ROS simplifies this by providing:
A modular architecture
Standard communication mechanisms
Hardware abstraction
Reusable packages
1.2 Evolution: ROS 1 vs ROS 2
ROS 2 was created to overcome limitations of ROS 1.
Feature
ROS 1
ROS 2
Real-time support
❌ No
✅ Yes
Multi-robot systems
Limited
Native support
Security
❌ None
✅ DDS Security
Windows support
❌ No
✅ Yes
Middleware
Custom
DDS-based
Production-ready
Research-focused
Industry-grade
Why ROS 2 matters for Physical AI
Physical AI systems need:
Reliability
Deterministic communication
Scalability
Safety
ROS 2 delivers all of these.
1.3 Core Concepts of ROS 2
Before writing any code, you must understand the ROS 2 mental model.
Key building blocks
Nodes
Topics
Services
Messages
Packages
Workspaces
We’ll explore each briefly here and deeply in later chapters.
1.4 Nodes: The Basic Execution Units
A node is a single executable that performs one task.
Examples:
Camera driver node
Obstacle detection node
Motor controller node
Why nodes?
Separation of concerns
Fault isolation
Reusability
Parallel execution
Example:
Instead of one huge program:
Camera Node
Image Processing Node
Navigation Node
Each node can be started, stopped, or replaced independently.
1.5 Communication in ROS 2
ROS 2 nodes communicate using middleware, not direct function calls.
Three main communication methods
Topics – asynchronous, continuous data
Services – synchronous, request/response
Actions – long-running tasks (covered later)
1.6 Topics (Publish–Subscribe Model)
Topics use a publisher–subscriber mechanism.
Publishers send messages
Subscribers receive messages
Nodes are loosely coupled
Example:
Camera node publishes images
Vision node subscribes to images
Display node subscribes to images
Topic Diagram
Copy code
Mermaid
graph LR
    CameraNode -->|/camera/image| VisionNode
    CameraNode -->|/camera/image| DisplayNode
Benefits:
Multiple subscribers
No direct dependency
Scalable
1.7 Services (Request–Response Model)
Services are used when:
You need a reply
The task is short and immediate
Example:
Ask robot for battery level
Reset odometry
Change robot mode
Service Diagram
Copy code
Mermaid
sequenceDiagram
    ClientNode->>ServiceNode: Request
    ServiceNode-->>ClientNode: Response
1.8 Messages: Data Containers
ROS 2 uses strongly typed messages.
Examples:
std_msgs/String
sensor_msgs/Image
geometry_msgs/Twist
A message is like a structured data packet.
Example structure:
Copy code
Text
geometry_msgs/Twist
- linear.x
- linear.y
- linear.z
- angular.x
- angular.y
- angular.z
1.9 DDS: The Backbone of ROS 2
ROS 2 is built on DDS (Data Distribution Service).
Why DDS?
Real-time support
Reliable delivery
Quality of Service (QoS)
Industry adoption (aerospace, defense)
Quality of Service (QoS)
QoS allows you to control:
Reliability (best effort vs reliable)
History (keep last N messages)
Durability (late joiners)
This is critical in Physical AI systems.
1.10 ROS 2 Architecture Overview
Copy code
Mermaid
graph TB
    Hardware --> Drivers
    Drivers --> ROS2Nodes
    ROS2Nodes --> DDS
    DDS --> ROS2Nodes
    ROS2Nodes --> Applications
1.11 ROS 2 Packages
A package is the basic unit of organization.
A package contains:
Nodes
Config files
Launch files
Dependencies
Why packages?
Code reuse
Dependency management
Modular design
Example packages:
rclpy – Python client library
navigation2 – Navigation stack
slam_toolbox – SLAM
1.12 Workspaces
A workspace is a directory where you build and manage packages.
Typical structure:
Copy code
Text
ros2_ws/
├── src/
│   └── my_package/
├── build/
├── install/
└── log/
You will create your own workspace in the next chapter.
1.13 Real-World Applications of ROS 2
Autonomous Vehicles
Sensor fusion
Localization
Path planning
Industrial Robotics
Robotic arms
Conveyor systems
Quality inspection
Drones
Flight control
Obstacle avoidance
Vision-based navigation
Healthcare Robotics
Surgical assistants
Rehabilitation robots
1.14 Simple ROS 2 Node Example (Preview)
Here’s a minimal Python ROS 2 node to show what’s coming.
Copy code
Python
import rclpy
from rclpy.node import Node

class HelloNode(Node):
    def _init_(self):
        super()._init_('hello_node')
        self.get_logger().info('Hello ROS 2!')

def main(args=None):
    rclpy.init(args=args)
    node = HelloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if _name_ == '_main_':
    main()
Don’t worry if this looks confusing—we’ll build it step by step in Chapter 3.
1.15 Common Beginner Mistakes
❌ Treating ROS like a normal Python app
❌ Ignoring node modularity
❌ Hardcoding parameters
❌ Not understanding topics vs services
ROS requires system-level thinking, not script-level thinking.
1.16 Practical Exercises
Exercise 1: Concept Check
Answer the following:
Why is ROS 2 better suited for industrial robots than ROS 1?
What is the difference between a node and a package?
When would you use a service instead of a topic?
Exercise 2: System Design
Design a ROS 2 system for a delivery robot with:
Camera
Motor controller
Obstacle detection
👉 List nodes and communication methods.
Exercise 3: Research Task
Find three companies using ROS 2 in production and note:
Industry
Robot type
ROS 2 use-case
1.17 Chapter Summary
In this chapter, you learned:
What ROS 2 is and why it exists
Core components of ROS 2
Nodes, topics, and services
DDS and QoS fundamentals
Real-world Physical AI applications
✅ Next Chapter
➡️ Chapter 2: ROS 2 Installation and Setup
You’ll install ROS 2, set up your workspace, and run your first real ROS 2 command.
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.get_logger().info('Node started!')

def main():
    rclpy.init()
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
\`\`\`

## Practical Exercise

Try this exercise...

## Summary

Key takeaways...

## Next Steps

Continue to [Next Chapter](./02-next-chapter.md)