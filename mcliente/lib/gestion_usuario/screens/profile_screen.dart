import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/inputs/app_input.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../repositories/user_repository.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _nitController = TextEditingController();
  
  bool _isLoading = true;
  bool _isSaving = false;
  UserModel? _user;
  final UserRepository _userRepository = UserRepository();

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final user = await _userRepository.fetchProfile();
      setState(() {
        _user = user;
        _nameController.text = user.nombre;
        _phoneController.text = user.telefono ?? '';
        _nitController.text = user.nit ?? '';
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      AppToast.showError(context, 'Error al cargar perfil');
    }
  }

  Future<void> _handleUpdate() async {
    if (_user == null || !_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);
    try {
      final updatedUser = await _userRepository.updateProfile(_user!.id, {
        'nombre': _nameController.text,
        'telefono': _phoneController.text,
        'nit': _nitController.text,
        'correo': _user!.correo, // El correo suele ser fijo o requiere otro flujo
      });
      setState(() {
        _user = updatedUser;
        _isSaving = false;
      });
      AppToast.showSuccess(context, 'Perfil actualizado');
    } catch (e) {
      setState(() => _isSaving = false);
      AppToast.showError(context, 'Error al actualizar');
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      userName: _user?.nombre ?? 'Cliente',
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.store,
          label: 'Explorar Tiendas',
          onTap: () => Navigator.pushReplacementNamed(context, '/tiendas'),
        ),
        AppSidebarItem(
          icon: Icons.storefront,
          label: 'Catálogo de Tienda',
          onTap: () => Navigator.pushReplacementNamed(context, '/tienda'),
        ),
        AppSidebarItem(
          icon: Icons.shopping_bag_outlined,
          label: 'Mis Pedidos',
          onTap: () => Navigator.pushReplacementNamed(context, '/pedidos'),
        ),
        AppSidebarItem(
          icon: Icons.person_outline,
          label: 'Mi Perfil',
          isActive: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/perfil'),
        ),
        AppSidebarItem(
          icon: Icons.logout,
          label: 'Salir',
          isLogout: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/login'),
        ),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Mi Perfil', style: AppTextStyles.h1),
          const SizedBox(height: 30),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else
            _buildProfileForm(),
        ],
      ),
    );
  }

  Widget _buildProfileForm() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 600),
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            CircleAvatar(
              radius: 50,
              backgroundColor: AppColors.accentTeal.withOpacity(0.1),
              child: const Icon(Icons.person, size: 50, color: AppColors.accentTeal),
            ),
            const SizedBox(height: 30),
            AppInput(
              label: 'Nombre Completo',
              controller: _nameController,
              labelIcon: Icons.person_outline,
              validator: (v) => v!.isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 20),
            AppInput(
              label: 'Correo Electrónico',
              controller: TextEditingController(text: _user?.correo),
              labelIcon: Icons.email_outlined,
              readOnly: true,
            ),
            const SizedBox(height: 20),
            AppInput(
              label: 'Teléfono',
              controller: _phoneController,
              labelIcon: Icons.phone_outlined,
            ),
            const SizedBox(height: 20),
            AppInput(
              label: 'NIT/CI',
              controller: _nitController,
              labelIcon: Icons.badge_outlined,
            ),
            const SizedBox(height: 40),
            AppButton.submit(
              label: 'Guardar Cambios',
              onPressed: _handleUpdate,
              isLoading: _isSaving,
            ),
          ],
        ),
      ),
    );
  }
}
