import struct
from enum import Enum


class Command(int, Enum):
    HELLO = 0
    I_AM_BRINGER = 1
    I_AM_FEEDER = 2
    MY_IP = 3
    MY_PORT = 4
    BRINGER = 5
    END = 6
    HI = 7
    COPY_THAT = 8
    WHO_YOU_KNOW = 9
    THAT_ALL = 10


"""
COMMUNICATION FLOW:
(bringer) HELLO         <-enum
(gossiper) HI           <-enum
(bringer) I_AM_BRINGER  <-enum
(bringer) test_node_1   <-str*
(gossiper) COPY_THAT    <-enum
(bringer) MY_IP         <-enum
(bringer) 127.0.0.1     <-int
(gossiper) COPY_THAT    <-enum
(bringer) MY_PORT       <-enum
(bringer) 40404         <-int
(gossiper) COPY_THAT    <-enum
(bringer)  WHO_YOU_KNOW <-enum
(gossiper) BRINGER      <-enum
(gossiper) 127.0.0.1    <-int
(gossiper) 40404        <-int
(bringer)  COPY_THAT    <-enum
(gossiper) BRINGER      <-enum
(gossiper) 127.0.0.2    <-int
(gossiper) 40444        <-int
(bringer)  COPY_THAT    <-enum
(gossiper) THAT_ALL     <-enum
(bringer)  BYE          <-enum
(gossiper) BYE          <-enum
"""
COMMAND_FORMAT = ">h"
SIZE_COMMAND_FORMAT = struct.calcsize(COMMAND_FORMAT)
NODE_NAME_FORMAT = ">10s"
SIZE_NODE_NAME_FORMAT = struct.calcsize(NODE_NAME_FORMAT)

MY_PORT_FORMAT = ">i"
SIZE_MY_PORT = struct.calcsize(MY_PORT_FORMAT)

MY_IP_FORMAT = ">i"
SIZE_MY_IP_FORMAT = struct.calcsize(MY_IP_FORMAT)
