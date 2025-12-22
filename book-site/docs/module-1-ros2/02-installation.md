---
sidebar_position: 2
---

ROS 2 Installation and Setup
Introduction

Before developing intelligent robotic systems with ROS 2, it is essential to establish a reliable and reproducible development environment. This chapter provides a comprehensive guide to installing, configuring, and verifying a ROS 2 setup suitable for research and production-grade Physical AI systems.

We cover supported operating systems, ROS 2 distributions, installation methods, workspace creation, dependency management, and common troubleshooting steps. By the end of this chapter, you will have a fully functional ROS 2 environment and understand why each setup step matters for scalable robotics development.

This chapter emphasizes ROS 2 Humble Hawksbill (Long-Term Support) on Ubuntu Linux, which is the most common setup in academia and industry.

Key Concepts
ROS 2 Distributions and Release Cycle

ROS 2 is released in named distributions, similar to Linux distributions. Each ROS 2 distribution is tied to:

A specific Ubuntu version

A defined support window

A set of tested core libraries

Common ROS 2 Distributions:

Distribution	Ubuntu	Support Type	Status
Foxy Fitzroy	20.04	LTS	EOL
Galactic	20.04	Short-term	EOL
Humble	22.04	LTS	✅ Recommended
Iron	22.04	Short-term	Active
Jazzy	24.04	LTS	Emerging

For Physical AI research, LTS distributions are preferred because they provide:

API stability

Security updates

Long-term reproducibility of experiments

Operating System Requirements

ROS 2 officially supports:

Ubuntu Linux (recommended)

Windows (limited tooling support)

macOS (experimental)

For this module:

OS: Ubuntu 22.04 LTS

Architecture: x86_64

Python: 3.10+

Linux is strongly preferred due to:

Native DDS networking

Better real-time performance

Strong community and driver support

ROS 2 Architecture Overview

ROS 2 uses a middleware-based architecture built on DDS (Data Distribution Service).

graph TD
    A[User Application] --> B[ROS 2 Client Library rclpy]
    B --> C[ROS 2 Core rcl]
    C --> D[DDS Middleware]
    D --> E[Network]
    E --> D


This architecture enables:

Distributed robotics

Real-time communication

Multi-robot systems

Fault tolerance

Understanding this stack helps diagnose installation and runtime issues.

Installation Methods

There are three primary ways to install ROS 2:

Binary Installation (APT) – Recommended

Source Installation – Advanced users

Docker-based Installation – Isolated environments

This chapter focuses on binary installation for reliability and ease of use.

ROS 2 Installation (Ubuntu 22.04)
Step 1: Configure Locale

ROS 2 requires UTF-8 locale support.

sudo apt update
sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

Step 2: Add ROS 2 Package Sources
sudo apt install software-properties-common
sudo add-apt-repository universe


Add the ROS 2 GPG key:

sudo apt update
sudo apt install curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg


Add the ROS 2 repository:

echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu \
$(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

Step 3: Install ROS 2 Humble
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop


The desktop package includes:

Core ROS 2 libraries

Visualization tools (RViz)

Demos and tutorials

Step 4: Environment Setup

Source the ROS 2 environment:

source /opt/ros/humble/setup.bash


To make this permanent:

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

Step 5: Verify Installation

Run a demo talker/listener:

ros2 run demo_nodes_cpp talker


In another terminal:

ros2 run demo_nodes_py listener


If messages are exchanged, your installation is successful.

ROS 2 Workspace Setup
What Is a Workspace?

A workspace is a directory where:

ROS 2 packages are developed

Code is built using colcon

Dependencies are resolved

Typical layout:

ros2_ws/
├── src/
│   └── my_package/
├── build/
├── install/
└── log/

Creating a Workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build


Source the workspace:

source install/setup.bash


Add to .bashrc (optional):

echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc

Workspace Overlay Concept
graph LR
    A[System ROS 2] --> B[Workspace Overlay]
    B --> C[Custom Packages]


Overlays allow:

Custom packages to override system ones

Multiple development layers

Clean separation of concerns

Dependency Management with rosdep

rosdep installs system dependencies automatically.

Initialize rosdep
sudo apt install python3-rosdep
sudo rosdep init
rosdep update

Install Dependencies
rosdep install --from-paths src --ignore-src -r -y


This is critical for:

Reproducible builds

CI/CD pipelines

Large multi-package systems

Code Example: Environment Verification Node
import rclpy
from rclpy.node import Node

class EnvironmentCheckNode(Node):
    def __init__(self):
        super().__init__('environment_check')
        self.get_logger().info('ROS 2 environment successfully configured!')

def main():
    rclpy.init()
    node = EnvironmentCheckNode()
    rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


This node verifies:

Python bindings

Runtime environment

Logging infrastructure

Practical Exercises
Exercise 1: Multi-Terminal Environment Check

Open two terminals

Source ROS 2 in one, not the other

Compare ros2 topic list

Question: Why does ROS 2 fail in the unsourced terminal?

Exercise 2: Workspace Overlay

Create two workspaces

Define a package with the same name in both

Observe which one is used

Exercise 3: Dependency Failure Simulation

Remove a system dependency

Attempt a build

Fix it using rosdep

Real-World Applications
Robotics Research Labs

Consistent ROS 2 installations across teams

Long-term experiment reproducibility

Autonomous Vehicles

Multiple ROS 2 workspaces for perception, planning, control

DDS-based networking across embedded devices

Industrial Automation

Stable LTS deployments

Secure package management

Cloud Robotics

ROS 2 inside Docker

CI pipelines using headless installations

Common Installation Issues and Debugging
Issue	Cause	Solution
ros2: command not found	Environment not sourced	Source setup.bash
DDS discovery failure	Firewall	Disable or configure
Build errors	Missing deps	Use rosdep
Python import errors	Wrong Python	Verify Python version
Summary

In this chapter, you:

Installed ROS 2 Humble on Ubuntu

Understood ROS 2 distributions and architecture

Created and configured a ROS 2 workspace

Learned dependency management with rosdep

Verified your environment using code and demos

A correct installation is the foundation for all ROS 2 development. Errors at this stage propagate into every layer of a robotic system, making careful setup essential.