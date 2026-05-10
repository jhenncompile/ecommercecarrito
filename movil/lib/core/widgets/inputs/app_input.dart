import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';

class AppInput extends StatelessWidget {
  final String label;
  final IconData? labelIcon;
  final String? hint;
  final bool obscureText;
  final TextEditingController? controller;
  final String? Function(String?)? validator;
  final Widget? suffixWidget;
  final bool readOnly;

  final void Function(String)? onChanged;

  const AppInput({
    super.key,
    required this.label,
    this.labelIcon,
    this.hint,
    this.obscureText = false,
    this.controller,
    this.validator,
    this.suffixWidget,
    this.readOnly = false,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                if (labelIcon != null) ...[
                  Icon(labelIcon, size: 16, color: AppColors.accentTeal),
                  const SizedBox(width: 8),
                ],
                Text(label, style: AppTextStyles.label),
              ],
            ),
            if (suffixWidget != null) suffixWidget!,
          ],
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          validator: validator,
          readOnly: readOnly,
          onChanged: onChanged,
          style: TextStyle(
            fontSize: 14, 
            color: readOnly ? AppColors.textGray : AppColors.textPrimary,
          ),
          decoration: InputDecoration(
            hintText: hint,
            filled: readOnly,
            fillColor: readOnly ? Colors.grey.shade100 : null,
          ),
        ),
      ],
    );
  }
}