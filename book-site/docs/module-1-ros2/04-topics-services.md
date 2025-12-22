---
sidebar_position: 4
---

Understanding Topics and Services
Introduction

Now that you can create and run ROS 2 nodes in VS Code, the next critical step is communication.
A single node is useful, but real robots are networks of nodes exchanging data continuously.

In ROS 2, nodes communicate using:

Topics → asynchronous data streams

Services → synchronous request–response calls

In this chapter, you will implement publishers, subscribers, and services in Python, run them from the VS Code terminal, and inspect live data using ROS 2 CLI tools.

Mental model:
Topics = data flow
Services = function calls over the network

Key Concepts
Topics: Asynchronous Communication

A topic is a named data channel where:

Publishers send messages

Subscribers receive messages

Communication is one-to-many

graph LR
    A[Publisher Node] -->|Topic| B[Subscriber Node]
    A -->|Topic| C[Subscriber Node]


Key properties of topics:

No direct coupling between nodes

High-frequency data support

Ideal for sensors, state, telemetry

Examples:

Camera images

Lidar scans

Robot pose

Velocity commands

Services: Synchronous Communication

A service follows a request–response model.

graph LR
    A[Client Node] -->|Request| B[Service Node]
    B -->|Response| A


Key properties of services:

Blocking or synchronous

Exactly one response per request

Ideal for configuration or commands

Examples:

Reset robot

Start/stop recording

Query system status

Message Types

Topics and services use strongly typed messages.

Examples:

std_msgs/msg/String

geometry_msgs/msg/Twist

sensor_msgs/msg/Image

Why typing matters:

Compile-time checks

Interoperability

Language independence

Working in VS Code: Create a New Package
Step 1: Open Terminal in VS Code
cd ~/ros2_ws/src

Step 2: Create Communication Package
ros2 pkg create ros2_comms \
  --build-type ament_python \
  --dependencies rclpy std_msgs


📁 VS Code folder structure:

ros2_comms/
├── ros2_comms/
│   └── __init__.py
├── setup.py
├── setup.cfg
└── package.xml

Topics in Practice
Creating a Publisher Node

📄 Create file:

ros2_comms/ros2_comms/talker.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    def __init__(self):
        super().__init__('talker_node')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        msg = String()
        msg.data = 'Hello from VS Code!'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')


def main():
    rclpy.init()
    node = TalkerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

Publisher Code Pointers

create_publisher()

Message type

Topic name

Queue size

Timer

Controls publish rate

QoS depth

Buffers messages

Creating a Subscriber Node

📄 Create file:

ros2_comms/ros2_comms/listener.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ListenerNode(Node):
    def __init__(self):
        super().__init__('listener_node')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')


def main():
    rclpy.init()
    node = ListenerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

Register Nodes in setup.py

Open setup.py and add:

entry_points={
    'console_scripts': [
        'talker = ros2_comms.talker:main',
        'listener = ros2_comms.listener:main',
    ],
},

Build and Run (VS Code Terminal)
cd ~/ros2_ws
colcon build
source install/setup.bash


Run in two VS Code terminals:

ros2 run ros2_comms talker

ros2 run ros2_comms listener

Inspecting Topics (Debugging)
List Topics
ros2 topic list

Echo Topic Data
ros2 topic echo /chatter

Topic Information
ros2 topic info /chatter


➡️ These tools are essential when debugging Physical AI pipelines.

Services in Practice
Creating a Service Node

📄 Create file:

ros2_comms/ros2_comms/add_two_ints_server.py

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback
        )

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(
            f'Request: {request.a} + {request.b} = {response.sum}'
        )
        return response


def main():
    rclpy.init()
    node = AddTwoIntsServer()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

Creating a Service Client

📄 Create file:

ros2_comms/ros2_comms/add_two_ints_client.py

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.client = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        self.send_request()

    def send_request(self):
        request = AddTwoInts.Request()
        request.a = 5
        request.b = 7
        self.future = self.client.call_async(request)
        self.future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        response = future.result()
        self.get_logger().info(f'Result: {response.sum}')
        rclpy.shutdown()


def main():
    rclpy.init()
    node = AddTwoIntsClient()
    rclpy.spin(node)

Register Service Nodes

Add to setup.py:

'add_server = ros2_comms.add_two_ints_server:main',
'add_client = ros2_comms.add_two_ints_client:main',

Run Services

In Terminal 1:

ros2 run ros2_comms add_server


In Terminal 2:

ros2 run ros2_comms add_client

Topics vs Services (Quick Comparison)
Feature	Topics	Services
Communication	Async	Sync
Many-to-many	Yes	No
Use case	Sensors, state	Commands
Blocking	No	Yes
Practical Exercise
Exercise 1: Topic Modification

Change topic name

Change publish frequency

Observe effect using ros2 topic hz

Exercise 2: Service Extension

Add input validation

Handle invalid requests

Log errors

Exercise 3: Multi-Node System

One publisher

Two subscribers

One service node

Real-World Applications
Autonomous Robots

Topics for sensor streams

Services for mission control

AI Pipelines

Topics feed ML inference

Services trigger model reloads

Industrial Automation

Services for configuration

Topics for monitoring

Cloud Robotics

Services exposed via bridges

Topics logged for analytics

Summary

In this chapter, you implemented ROS 2 communication from inside VS Code.

You learned:

How topics work

How to publish and subscribe

How services differ from topics

How to debug communication

How to design scalable node networks

Communication is the nervous system of Physical AI.
Poor communication design leads to fragile robots.