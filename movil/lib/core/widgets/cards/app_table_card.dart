import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class AppTableCard extends StatelessWidget {
  final String title;
  final List<String> columns;
  final List<List<Widget>> rows;

  const AppTableCard({
    super.key,
    required this.title,
    required this.columns,
    required this.rows,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        boxShadow: AppShadows.card,
      ),
      padding: EdgeInsets.all(MediaQuery.of(context).size.width < 600 ? 15 : 25),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTextStyles.h3),
          const SizedBox(height: 20),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minWidth: columns.length <= 3 
                    ? MediaQuery.of(context).size.width - 50 
                    : (MediaQuery.of(context).size.width < 600 ? 600 : MediaQuery.of(context).size.width - 50),
              ),
              child: Table(
                columnWidths: const {0: FlexColumnWidth()},
                border: const TableBorder(
                  horizontalInside: BorderSide(color: AppColors.bgSearch, width: 1),
                ),
                children: [
                  // Header row
                  TableRow(
                    children: columns.map((col) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                        child: Text(col, style: AppTextStyles.statLabel.copyWith(fontWeight: FontWeight.w600)),
                      );
                    }).toList(),
                  ),
                  // Data rows
                  ...rows.map((cells) => TableRow(
                        children: cells.map((cell) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 12),
                            child: cell,
                          );
                        }).toList(),
                      )),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}