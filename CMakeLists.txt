cmake_minimum_required(VERSION 3.8)
project(Banyan)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES Socket.h Socket.cpp)
add_executable(Banyan ${SOURCE_FILES})
