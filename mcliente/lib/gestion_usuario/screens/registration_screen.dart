import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/inputs/app_input.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../repositories/auth_repository.dart';

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _nitController = TextEditingController();
  final _passwordController = TextEditingController();
  
  bool _isLoading = false;
  final AuthRepository _authRepository = AuthRepository();

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    
    final success = await _authRepository.register({
      'nombre': _nameController.text,
      'correo': _emailController.text,
      'telefono': _phoneController.text,
      'nit': _nitController.text,
      'contrasena': _passwordController.text,
    });

    setState(() => _isLoading = false);

    if (success) {
      if (!mounted) return;
      AppToast.showSuccess(context, '¡Cuenta creada con éxito!');
      Navigator.pushReplacementNamed(context, '/tiendas');
    } else {
      if (!mounted) return;
      AppToast.showError(context, 'Error en el registro');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgLight,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(20),
              boxShadow: const [
                BoxShadow(color: Colors.black12, blurRadius: 20, offset: Offset(0, 10)),
              ],
            ),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      padding: const EdgeInsets.all(15),
                      decoration: const BoxDecoration(color: AppColors.accentTeal, shape: BoxShape.circle),
                      child: const Icon(Icons.person_add_outlined, color: Colors.white, size: 30),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Center(
                    child: Text('Crea tu cuenta', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(height: 10),
                  const Center(
                    child: Text('Únete a nuestra comunidad de compradores', style: TextStyle(color: AppColors.textMuted)),
                  ),
                  const SizedBox(height: 30),
                  AppInput(
                    label: 'Nombre Completo',
                    controller: _nameController,
                    labelIcon: Icons.person_outline,
                    validator: (v) => v!.isEmpty ? 'Requerido' : null,
                  ),
                  const SizedBox(height: 15),
                  AppInput(
                    label: 'Correo Electrónico',
                    controller: _emailController,
                    labelIcon: Icons.email_outlined,
                    validator: (v) => v!.isEmpty ? 'Requerido' : null,
                  ),
                  const SizedBox(height: 15),
                  AppInput(
                    label: 'Teléfono',
                    controller: _phoneController,
                    labelIcon: Icons.phone_outlined,
                  ),
                  const SizedBox(height: 15),
                  AppInput(
                    label: 'NIT / CI (Opcional)',
                    controller: _nitController,
                    labelIcon: Icons.badge_outlined,
                  ),
                  const SizedBox(height: 15),
                  AppInput(
                    label: 'Contraseña',
                    controller: _passwordController,
                    labelIcon: Icons.lock_outline,
                    obscureText: true,
                    validator: (v) => v!.length < 6 ? 'Mínimo 6 caracteres' : null,
                  ),
                  const SizedBox(height: 30),
                  AppButton.submit(
                    label: 'Registrarse',
                    onPressed: _handleRegister,
                    isLoading: _isLoading,
                  ),
                  const SizedBox(height: 20),
                  Center(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('¿Ya tienes cuenta? Inicia sesión', style: TextStyle(color: AppColors.accentTeal)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
