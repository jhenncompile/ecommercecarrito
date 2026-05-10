import 'dart:convert';
import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/storage/secure_storage.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';

class ShopListScreen extends StatefulWidget {
  const ShopListScreen({super.key});

  @override
  State<ShopListScreen> createState() => _ShopListScreenState();
}

class _ShopListScreenState extends State<ShopListScreen> {
  final ApiClient _apiClient = ApiClient();
  final AuthRepository _authRepository = AuthRepository();
  final SecureStorageService _storage = SecureStorageService();
  
  List<dynamic> _shops = [];
  bool _isLoading = true;
  String _userName = 'Invitado';

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    String decodedUser = 'Invitado';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      try {
        final parts = token.split('.');
        if (parts.length == 3) {
          var payload = parts[1];
          while (payload.length % 4 != 0) payload += '=';
          final data = jsonDecode(utf8.decode(base64Url.decode(payload)));
          decodedUser = data['full_name'] ?? data['username'] ?? 'Invitado';
        }
      } catch (e) {
        // Ignorar
      }
    }

    setState(() {
      _userName = decodedUser;
    });

    await _cargarTiendas();
  }

  Future<void> _cargarTiendas() async {
    try {
      final response = await _apiClient.get('${ApiConstants.mainBaseUrl}/tiendas-publicas/', requiresAuth: false);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _shops = data['results'] ?? data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _entrarTienda(dynamic shop) async {
    // Guardar el tenant de la tienda seleccionada
    final schema = shop['schema_name'];
    final subdomain = shop['subdominio'] ?? schema;
    await _storage.saveTenantInfo(schema, subdomain);
    
    // Navegar al catálogo de la tienda
    if (!mounted) return;
    Navigator.pushReplacementNamed(context, '/tienda');
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: 'Explorar',
      userName: _userName,
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.store,
          label: 'Explorar Tiendas',
          isActive: true,
          onTap: () {},
        ),
        AppSidebarItem(
          icon: Icons.shopping_bag_outlined,
          label: 'Mis Pedidos',
          onTap: () => Navigator.pushReplacementNamed(context, '/pedidos'),
        ),
        AppSidebarItem(
          icon: Icons.person_outline,
          label: 'Mi Perfil',
          onTap: () => Navigator.pushReplacementNamed(context, '/perfil'),
        ),
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
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Explorar Tiendas', style: AppTextStyles.h1),
          const SizedBox(height: 5),
          Text('Encuentra los mejores productos en nuestra red', style: AppTextStyles.subtitle),
          const SizedBox(height: 30),
          
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_shops.isEmpty)
            const Center(child: Text('No hay tiendas disponibles.'))
          else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: MediaQuery.of(context).size.width > 1200 ? 4 : (MediaQuery.of(context).size.width > 800 ? 3 : 2),
                crossAxisSpacing: 20,
                mainAxisSpacing: 20,
                childAspectRatio: 0.85,
              ),
              itemCount: _shops.length,
              itemBuilder: (context, index) {
                final shop = _shops[index];
                return _buildShopCard(shop);
              },
            ),
        ],
      ),
    );
  }

  Widget _buildShopCard(dynamic shop) {
    return GestureDetector(
      onTap: () => _entrarTienda(shop),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.bgCard,
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: AppColors.border),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: const BoxDecoration(
                  color: AppColors.bgSearch,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
                ),
                child: shop['icono'] != null 
                    ? ClipRRect(
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                        child: Image.network(shop['icono'], fit: BoxFit.cover),
                      )
                    : shop['logo_url'] != null
                        ? ClipRRect(
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                            child: Image.network(shop['logo_url'], fit: BoxFit.cover),
                          )
                        : const Icon(Icons.store, size: 50, color: AppColors.textMuted),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(15),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (shop['categoria_tienda'] != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        color: AppColors.accentTeal.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        shop['categoria_tienda'], 
                        style: const TextStyle(color: AppColors.accentTeal, fontSize: 10, fontWeight: FontWeight.bold)
                      ),
                    ),
                  Text(
                    shop['nombre_comercial'] ?? shop['schema_name'] ?? 'Tienda', 
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppColors.primaryDark), 
                    maxLines: 1, 
                    overflow: TextOverflow.ellipsis
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: const [
                      Icon(Icons.login, size: 14, color: AppColors.accentTeal),
                      SizedBox(width: 5),
                      Text('Visitar tienda', style: TextStyle(color: AppColors.accentTeal, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
