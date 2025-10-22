# pydebroglie-cli

**pydebroglie-cli** is the CLI frontend of `pydebroglie`, the pure Python reimplementation of the wonderful [DeBroglie](https://github.com/BorisTheBrave/DeBroglie) library in C# created by [BorisTheBrave](https://github.com/BorisTheBrave).

It aims to use the same internal classes naming and try to be compatible with [the original documentation](https://boristhebrave.github.io/DeBroglie/).

The tool is bundled under 2 packages:
 - The library: `pydebroglie`
 - The CLI frontend: `pydebroglie-cli`

## Description

DeBroglie is a C# library implementing the Wave Function Collapse algorithm with support for additional non-local constraints, and other useful features.

Wave Function Collapse (WFC) is an constraint-based algorithm for generating new images that are locally similar to a sample bitmap. It can also operate on tilesets, generating tilemaps where the tile adjacency fits a specification.

Unlike the original WFC implementation, De Broglie has full backtracking support, so can solve arbitrarily complicated sets of constraints. It is still optimized towards local constraints.

## Features

 - "Overlapped" model implementation of WFC
 - Non-local constraints allow you to specify other desired properties of the result
 - Backtracking support - the original WFC implementation immediately give up when a contradiction occurs.
 - Supports 2d tiles, hexs, and 3d voxels

## Usage 

See https://boristhebrave.github.io/DeBroglie/ (original C# documentation, should be compatible with this implementation)
