import 'package:flutter/material.dart';

class AppCanvas extends StatefulWidget {
  const AppCanvas({super.key});

  @override
  State<AppCanvas> createState() => _AppCanvasState();
}

class _AppCanvasState extends State<AppCanvas> {
  final List<List<bool>> filledSquares = [];

  late double screenWidth;
  late double screenHeight;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    screenWidth = MediaQuery.sizeOf(context).width;
    screenHeight = MediaQuery.sizeOf(context).height;
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: double.infinity,
        height: screenHeight / 2,
        child: GestureDetector(
          onTapDown: (details) {
            final position = details.localPosition / 10;
            final squareX = position.dx.floorToDouble() + 1;
            final squareY = position.dy.floorToDouble() + 1;
            final square = Offset(squareY, squareY);

            print('square X: $squareX');
            print('square Y: $squareY');

            _onSquarePressed(square);
          },
          child: CustomPaint(
            painter: CanvasPainter(filledSquares: filledSquares),
          ),
        ),
      ),
    );
  }

  void _onSquarePressed(Offset square) {
    // TODO(st1llsane)
  }
}

class CanvasPainter extends CustomPainter {
  CanvasPainter({required this.filledSquares});

  final List<List<bool>> filledSquares;

  @override
  void paint(Canvas canvas, Size size) {
    _drawLattice(canvas, size);
  }

  // TODO(st1llsane): Read about `drawAtlas method`
  // 1 square = 10 logical pixels
  void _drawLattice(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey
      ..strokeWidth = 1;

    final longestSide = size.longestSide;

    for (double i = 0; i <= longestSide; i += 10) {
      canvas
        ..drawLine(Offset(i, 0), Offset(i, longestSide), paint)
        ..drawLine(Offset(0, i), Offset(longestSide, i), paint);
    }
  }

  void _fillSquares(Canvas canvas) {}

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
