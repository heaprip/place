import 'package:flutter/material.dart';
import 'package:place_flutter/canvas/app_canvas.dart';

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(body: SafeArea(child: AppCanvas())),
    );
  }
}
