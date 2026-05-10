import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/widgets/cards/app_login_card.dart'; 
import '../../core/widgets/feedback/app_toast.dart';
import '../repositories/auth_repository.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final AuthRepository _authRepository = AuthRepository();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      AppToast.showError(context, 'Por favor, completa todos los campos.');
      return;
    }

    setState(() => _isLoading = true);
    final bool isSuccess = await _authRepository.login(email, password);
    setState(() => _isLoading = false); 

    if (isSuccess) {
      if (!mounted) return;
      AppToast.showSuccess(context, '¡Bienvenido de vuelta!');
      Navigator.pushReplacementNamed(context, '/tiendas'); 
    } else {
      if (!mounted) return;
      AppToast.showError(context, 'Correo o contraseña incorrectos.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgLight,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: _isLoading 
              ? const CircularProgressIndicator(color: AppColors.accentTeal)
              : AppLoginCard(
                  brandName: 'MiQhatu',
                  brandIcon: Icons.shopping_bag_outlined,
                  infoTitle: 'Tu tienda favorita,\nahora en tu bolsillo.',
                  infoSubtitle: 'Explora productos, realiza pedidos y haz seguimiento a tus compras.',
                  emailController: _emailController,
                  passwordController: _passwordController,
                  onSubmit: _handleLogin,
                  onForgot: () {
                    Navigator.pushNamed(context, '/recuperar-password');
                  },
                  onRegister: () {
                    Navigator.pushNamed(context, '/registro');
                  },
                ),
        ),
      ),
    );
  }
}
