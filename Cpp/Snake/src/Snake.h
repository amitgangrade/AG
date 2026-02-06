#pragma once
#include <deque>
#include "raylib.h"

struct Point {
    int x;
    int y;
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
};

class Snake {
public:
    Snake();
    void Draw();
    void Update();
    void Reset();
    void Grow();
    
    std::deque<Point> body;
    Point direction;
    bool addSegment;
    Color color;
};
