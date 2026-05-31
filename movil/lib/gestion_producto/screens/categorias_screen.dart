import 'dart:convert';
import 'package:flutter/material.dart';

// UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/cards/app_table_card.dart';

// Lógica
import '../models/category_model.dart';
import '../../dashboard/repositories/product_repository.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';

class CategoriasScreen extends StatefulWidget {
  const CategoriasScreen({super.key});

  @override
  State<CategoriasScreen> createState() => _CategoriasScreenState();
}

class _CategoriasScreenState extends State<CategoriasScreen> {
  List<CategoryModel> _categories = [];
  bool _isLoading = true;
  String? _error;

  String _storeName = 'Cargando...';
  String _userName = 'Admin';

  final ProductRepository _productRepository = ProductRepository();
  final AuthRepository _authRepository = AuthRepository();

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    final schemaName = await _authRepository.getSchemaName();
    String decodedUser = 'Admin';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      final payload = _decodeJwt(token);
      if (payload != null) {
        decodedUser = payload['full_name'] ?? payload['username'] ?? 'Admin';
      }
    }

    setState(() {
      _storeName = _formatStoreName(schemaName ?? '');
      _userName = decodedUser;
    });

    await _cargarCategorias();
  }

  String _formatStoreName(String schema) {
    if (schema.isEmpty) return 'Mi Tienda';
    return schema.split(RegExp(r'[x_]+')).map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  Map<String, dynamic>? _decodeJwt(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      var payload = parts[1];
      while (payload.length % 4 != 0) {
        payload += '=';
      }
      return jsonDecode(utf8.decode(base64Url.decode(payload)));
    } catch (_) {
      return null;
    }
  }

  Future<void> _cargarCategorias() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final cats = await _productRepository.fetchCategories();
      setState(() {
        _categories = cats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  void _abrirFormulario({CategoryModel? category}) async {
    final nameController = TextEditingController(text: category?.nombre ?? '');
    int? selectedParentId = category?.parent;

    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: Text(category == null ? 'Nueva Categoría' : 'Editar Categoría'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: nameController,
                    style: const TextStyle(color: AppColors.textPrimary),
                    decoration: const InputDecoration(labelText: 'Nombre', hintText: 'Ej: Gaseosas'),
                    autofocus: true,
                  ),
                  const SizedBox(height: 20),
                  DropdownButtonFormField<int?>(
                    value: selectedParentId,
                    decoration: const InputDecoration(labelText: 'Categoría Padre (Opcional)'),
                    style: const TextStyle(color: AppColors.textPrimary),
                    items: [
                      const DropdownMenuItem<int?>(value: null, child: Text('Ninguna (Categoría Principal)')),
                      ..._categories
                          .where((c) => c.id != category?.id) // No puede ser su propio padre
                          .map((c) => DropdownMenuItem<int?>(
                                value: c.id,
                                child: Text(c.rutaCompleta ?? c.nombre),
                              )),
                    ],
                    onChanged: (v) => setDialogState(() => selectedParentId = v),
                  ),
                ],
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
                AppButton.primary(
                  label: category == null ? 'Crear' : 'Actualizar',
                  onPressed: () => Navigator.pop(context, true),
                ),
              ],
            );
          }
        );
      },
    );

    if (result == true && nameController.text.isNotEmpty) {
      try {
        final catData = CategoryModel(
          id: category?.id ?? 0, 
          nombre: nameController.text, 
          descripcion: '',
          parent: selectedParentId,
        );
        if (category == null) {
          await _productRepository.createCategory(catData);
        } else {
          await _productRepository.updateCategory(category.id, catData);
        }
        _cargarCategorias();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      }
    }
  }

  Future<void> _confirmarEliminacion(CategoryModel cat) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar Categoría'),
        content: Text('¿Estás seguro de que deseas eliminar "${cat.nombre}"? Esto podría afectar a los productos asociados.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _productRepository.deleteCategory(cat.id);
        _cargarCategorias();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: _userName,
      sidebarItems: [
        AppSidebarItem(icon: Icons.dashboard, label: 'Panel', onTap: () => Navigator.pushReplacementNamed(context, '/dashboard')),
        AppSidebarItem(icon: Icons.inventory_2, label: 'Productos', onTap: () => Navigator.pushReplacementNamed(context, '/productos')),
        AppSidebarItem(icon: Icons.category, label: 'Categorías', isActive: true, onTap: () => Navigator.pushReplacementNamed(context, '/categorias')),
        AppSidebarItem(icon: Icons.list_alt, label: 'Inventario', onTap: () => Navigator.pushReplacementNamed(context, '/inventario')),
        AppSidebarItem(icon: Icons.shopping_cart, label: 'Ventas', onTap: () => Navigator.pushReplacementNamed(context, '/ventas')),
        AppSidebarItem(icon: Icons.people, label: 'Clientes', onTap: () => Navigator.pushReplacementNamed(context, '/clientes')),
        AppSidebarItem(icon: Icons.bar_chart, label: 'Reportes', onTap: () => Navigator.pushReplacementNamed(context, '/reportes')),
        AppSidebarItem(icon: Icons.settings, label: 'Configuración', onTap: () => Navigator.pushReplacementNamed(context, '/configuracion')),
        AppSidebarItem(
          icon: Icons.logout,
          label: 'Salir',
          isLogout: true,
          onTap: () async {
            await _authRepository.logout();
            if (!context.mounted) return;
            Navigator.pushReplacementNamed(context, '/login');
          },
        ),
        AppSidebarItem(
          icon: Icons.trending_up,
          label: 'Predicciones',
          onTap: () => Navigator.pushReplacementNamed(context, '/predicciones'),
        ),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              final isMobile = constraints.maxWidth < 600;
              if (isMobile) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Categorías', style: AppTextStyles.h1.copyWith(fontSize: 28)),
                    const SizedBox(height: 5),
                    Text('Organiza tus productos', style: AppTextStyles.subtitle),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: AppButton.add(
                        label: 'Nueva Categoría',
                        icon: Icons.add,
                        onPressed: () => _abrirFormulario(),
                      ),
                    ),
                  ],
                );
              }
              return Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Categorías', style: AppTextStyles.h1),
                      const SizedBox(height: 5),
                      Text('Organiza tus productos por grupos', style: AppTextStyles.subtitle),
                    ],
                  ),
                  AppButton.add(
                    label: 'Nueva Categoría',
                    icon: Icons.add,
                    onPressed: () => _abrirFormulario(),
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 30),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_error != null)
            Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
          else
            AppTableCard(
              title: 'Listado de Categorías',
              columns: const ['ID', 'Nombre', 'Estado', 'Acciones'],
              rows: _categories.map((cat) {
                return [
                  Text('#${cat.id}', style: const TextStyle(color: AppColors.textMuted)),
                  Text(cat.rutaCompleta ?? cat.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                  cat.activo ? const Text('Activo', style: TextStyle(color: Colors.green)) : const Text('Inactivo', style: TextStyle(color: Colors.grey)),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit_outlined, color: AppColors.accentTeal, size: 20),
                        onPressed: () => _abrirFormulario(category: cat),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.delete_outline, color: AppColors.danger, size: 20),
                        onPressed: () => _confirmarEliminacion(cat),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                ];
              }).toList(),
            ),
        ],
      ),
    );
  }
}
