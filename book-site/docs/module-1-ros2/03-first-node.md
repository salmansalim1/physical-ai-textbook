---
sidebar_position: 3
---

Creating Your First ROS 2 Node
Introduction

At this point, ROS 2 is installed, your workspace is ready, and VS Code is open.
Now we move from setup to actual development.

In ROS 2, everything runs inside nodes. A node is a single executable program that performs a well-defined task such as:

Reading sensor data

Running an AI model

Sending commands to motors

In this chapter, you will write your first ROS 2 node in Python, run it from the terminal inside VS Code, and inspect it using ROS 2 command-line tools.

Mindset: Think of a node as a microservice for robotics.

Key Concepts
What Is a ROS 2 Node?

A ROS 2 node is:

A process

With a unique name

That communicates with other nodes via ROS 2 middleware

Key properties of nodes:

Modular → one responsibility per node

Distributed → can run on different machines

Replaceable → easy to swap implementations

graph LR
    A[Sensor Node] --> B[Perception Node]
    B --> C[Planning Node]
    C --> D[Control Node]


➡️ This separation is critical in Physical AI, where perception, reasoning, and control evolve independently.

Node Lifecycle (High-Level)

Every ROS 2 node follows this execution flow:

stateDiagram-v2
    [*] --> Init
    Init --> Running
    Running --> Shutdown
    Shutdown --> [*]


In practice:

rclpy.init() → ROS system starts

Node constructor → node registers itself

rclpy.spin() → node waits and reacts

rclpy.shutdown() → clean exit

rclpy (Python Client Library)

You will write nodes using rclpy, which provides:

Node APIs

Logging

Timers

Communication primitives

Why Python here?

Fast prototyping

AI/ML integration

Research-friendly

⚠️ Python is not hard real-time—but perfect for high-level intelligence.

VS Code Workflow Setup
Step 1: Open Your Workspace in VS Code
cd ~/ros2_ws
code .


In VS Code:

Open Explorer

You should see src/, build/, install/

Creating a Python ROS 2 Package
Step 2: Create Package (Terminal in VS Code)
cd src
ros2 pkg create my_first_node \
  --build-type ament_python \
  --dependencies rclpy


📁 VS Code will now show:

my_first_node/
├── my_first_node/
│   └── __init__.py
├── resource/
├── setup.py
├── setup.cfg
└── package.xml


Important files:

setup.py → entry points

package.xml → dependencies

Python folder → your node code

Code Example: Your First ROS 2 Node
Step 3: Create Node File

Inside:

my_first_node/my_first_node/


Create a new file:

hello_node.py

Node Code (Type This in VS Code)
import rclpy
from rclpy.node import Node


class HelloNode(Node):
    def __init__(self):
        super().__init__('hello_node')
        self.get_logger().info('Hello from my first ROS 2 node!')


def main():
    rclpy.init()
    node = HelloNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

Code Breakdown (Pointer Style)

rclpy.init()

Starts ROS 2 communication

Node

Base class for all ROS 2 nodes

Node name (hello_node)

Must be unique at runtime

get_logger()

ROS-native logging (better than print)

rclpy.spin()

Keeps the node alive

Registering the Node (setup.py)

Open setup.py and update entry points:

entry_points={
    'console_scripts': [
        'hello_node = my_first_node.hello_node:main',
    ],
},


➡️ This tells ROS 2:

Executable name: hello_node

Python function: main

Build and Run (Inside VS Code Terminal)
Step 4: Build Workspace
cd ~/ros2_ws
colcon build


Source environment:

source install/setup.bash

Step 5: Run the Node
ros2 run my_first_node hello_node


✅ Expected output:

[INFO] [hello_node]: Hello from my first ROS 2 node!

Inspecting the Node (Debugging Like a Pro)
List Active Nodes
ros2 node list


Output:

/hello_node

Get Node Details
ros2 node info /hello_node


You’ll see:

Publishers

Subscribers

Services

Parameters

➡️ This is essential for debugging distributed systems.

Adding a Timer (Realistic Node Behavior)

Most nodes do not run once — they run repeatedly.

class TimerNode(Node):
    def __init__(self):
        super().__init__('timer_node')
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info('Running every second')


Key ideas:

create_timer() → periodic execution

Callback → control loops, monitoring, AI inference

Practical Exercise
Exercise 1: Modify the Node

Change node name

Change log message

Add a 2-second timer

Exercise 2: Run Multiple Nodes

Open two VS Code terminals

Run the same node twice

Observe name collision

Fix using:

ros2 run my_first_node hello_node --ros-args -r __node:=hello_node_2

Exercise 3: Crash & Recover

Add an exception inside callback

Observe behavior

Add try–except handling

Real-World Applications
AI-Based Robotics

Python nodes for:

Vision models

LLM-based planners

Sensor fusion

Autonomous Vehicles

One node per subsystem

Clear fault isolation

Industrial Robots

Modular nodes = easier maintenance

Hot-swapping faulty components

Research Prototypes

Rapid iteration inside VS Code

Debugging with logs and CLI tools

Summary

In this chapter, you coded your first ROS 2 node in VS Code.

You learned:

What a node is

How to create a Python ROS 2 package

How to write, register, build, and run a node

How to inspect nodes at runtime

How timers enable continuous behavior

Nodes are the building blocks of Physical AI systems.
Without mastering nodes, scalable robotics is impossible.