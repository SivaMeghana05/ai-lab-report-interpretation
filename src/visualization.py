import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import logging

logger = logging.getLogger("HealthLensAI.Visualization")

class VisualizationService:
    """Enhanced visualization service with improved charts"""
    
    def create_health_score_chart(self, score):
        """Create enhanced health score gauge chart"""
        plt.clf()  # Clear any existing plots
        fig, ax = plt.subplots(figsize=(5, 2.5), dpi=100)
        
        # Create gradient colormap
        cmap = plt.cm.RdYlGn
        norm = plt.Normalize(0, 100)
        
        # Background bar
        plt.barh([0], [100], color='lightgray', height=0.5, alpha=0.3)
        
        # Score bar with gradient color
        plt.barh([0], [score], color=cmap(norm(score)), height=0.5)
        
        # Add score markers
        for i in range(0, 101, 20):
            plt.axvline(x=i, color='white', linestyle='-', alpha=0.3, linewidth=0.5)
            if i > 0:  # Skip 0 label
                plt.text(i, -0.8, str(i), ha='center', va='center', fontsize=8, alpha=0.7)
        
        # Add health categories
        categories = [
            (0, 20, "Poor", "red"),
            (20, 40, "Fair", "orange"),
            (40, 60, "Moderate", "yellow"),
            (60, 80, "Good", "lightgreen"),
            (80, 100, "Excellent", "green")
        ]
        
        for start, end, label, color in categories:
            mid = (start + end) / 2
            plt.annotate(label, xy=(mid, 0.8), xytext=(mid, 1.2),
                        ha='center', va='center', fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.3", fc=color, ec="none", alpha=0.6))
            
            # Highlight current category
            if start <= score <= end:
                plt.annotate("▼", xy=(score, 0.9), xytext=(score, 0.9),
                            ha='center', va='center', fontsize=12,
                            color='black', alpha=0.7)
        
        # Add score text
        plt.text(score, 0, f'{score}',
                ha='center', va='center', fontsize=14, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle="round,pad=0.3"))
        
        # Customize chart appearance
        plt.xlim(-5, 105)
        plt.ylim(-1, 1.5)
        plt.axis('off')
        plt.title("Health Score", fontsize=12, fontweight='bold', pad=10)
        
        plt.tight_layout()
        return fig
    
    def create_severity_chart(self, df):
        """Create enhanced severity distribution chart"""
        plt.clf()  # Clear any existing plots
        
        # Ensure Severity column exists
        if 'Severity' not in df.columns:
            # Add Severity based on Status
            df['Severity'] = df.apply(lambda row: 'None' if row.get('Status', '') == 'Normal' else 'Moderate', axis=1)
        
        # Count severities
        severity_counts = df['Severity'].value_counts()
        
        # Define colors and order
        severity_order = ['Severe', 'Moderate', 'Mild', 'None']
        colors = {
            'Severe': '#FF5757',
            'Moderate': '#FFA500', 
            'Mild': '#5D9CEC',
            'None': '#7ED957'
        }
        
        # Reindex to ensure consistent order
        severity_counts = severity_counts.reindex(severity_order, fill_value=0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        # Create horizontal bars with enhanced styling
        bars = plt.barh(
            severity_order,
            severity_counts.values,
            color=[colors.get(x, '#CCCCCC') for x in severity_order],
            height=0.6,
            alpha=0.8
        )
        
        # Add count and percentage labels
        total = severity_counts.sum()
        for i, bar in enumerate(bars):
            count = severity_counts.values[i]
            if count > 0:
                percentage = (count / total) * 100
                plt.text(
                    count + 0.1,
                    i,
                    f"{int(count)} ({percentage:.1f}%)",
                    va='center',
                    fontsize=9
                )
        
        # Add severity descriptions
        descriptions = {
            'Severe': 'Requires immediate attention',
            'Moderate': 'Follow up recommended',
            'Mild': 'Monitor over time',
            'None': 'Within normal range'
        }
        
        # Add a second y-axis for descriptions
        ax2 = ax.twinx()
        ax2.set_yticks(range(len(severity_order)))
        ax2.set_yticklabels([descriptions.get(s, '') for s in severity_order], fontsize=8)
        ax2.set_ylim(ax.get_ylim())
        
        # Customize chart appearance
        plt.title('Test Result Severity Distribution', fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Tests', fontsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_category_chart(self, df):
        """Create enhanced test category distribution chart"""
        plt.clf()  # Clear any existing plots
        
        # Ensure required columns exist
        if 'Category' not in df.columns:
            df['Category'] = 'Other Tests'
        if 'Status' not in df.columns:
            df['Status'] = 'Normal'
        
        # Get category counts
        category_counts = df['Category'].value_counts()
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        
        # Create pie chart
        wedges, texts, autotexts = ax1.pie(
            category_counts.values,
            labels=None,
            autopct='',
            startangle=90,
            wedgeprops=dict(width=0.5, edgecolor='w'),
            colors=plt.cm.Pastel1(np.linspace(0, 1, len(category_counts)))
        )
        
        # Add legend
        ax1.legend(
            wedges,
            [f"{cat} ({count})" for cat, count in zip(category_counts.index, category_counts.values)],
            title="Categories",
            loc="center left",
            bbox_to_anchor=(0.9, 0.5),
            fontsize=9
        )
        
        # Add title
        ax1.set_title('Test Categories Distribution', fontsize=12, fontweight='bold')
        
        # Create abnormal tests by category chart
        abnormal_by_category = {}
        normal_by_category = {}
        
        for category in category_counts.index:
            category_df = df[df['Category'] == category]
            abnormal_count = len(category_df[category_df['Status'] != 'Normal'])
            normal_count = len(category_df) - abnormal_count
            abnormal_by_category[category] = abnormal_count
            normal_by_category[category] = normal_count
        
        # Sort categories by abnormal count
        sorted_categories = sorted(
            abnormal_by_category.keys(),
            key=lambda x: abnormal_by_category[x],
            reverse=True
        )
        
        # Create stacked bar chart
        abnormal_values = [abnormal_by_category[cat] for cat in sorted_categories]
        normal_values = [normal_by_category[cat] for cat in sorted_categories]
        
        ax2.barh(sorted_categories, abnormal_values, color='#FF9999', label='Abnormal')
        ax2.barh(sorted_categories, normal_values, left=abnormal_values, color='#99CC99', label='Normal')
        
        # Add count labels
        for i, category in enumerate(sorted_categories):
            total = abnormal_by_category[category] + normal_by_category[category]
            abnormal_pct = (abnormal_by_category[category] / total) * 100 if total > 0 else 0
            
            if abnormal_by_category[category] > 0:
                ax2.text(
                    abnormal_by_category[category] / 2,
                    i,
                    f"{abnormal_pct:.0f}%",
                    ha='center',
                    va='center',
                    color='white',
                    fontsize=8,
                    fontweight='bold'
                )
        
        # Customize chart appearance
        ax2.set_title('Abnormal Tests by Category', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Number of Tests', fontsize=10)
        ax2.legend(loc='upper right', fontsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_trend_chart(self, test_name, current_value, previous_values):
        """Create enhanced trend chart for a specific test"""
        plt.clf()  # Clear any existing plots
        
        try:
            # Handle both string and dictionary previous values
            processed_values = []
            for v in previous_values:
                try:
                    if isinstance(v, dict):
                        if 'value' in v:
                            value_str = v['value']
                        elif 'Value' in v:
                            value_str = v['Value']
                        else:
                            continue
                    else:
                        value_str = v
                    
                    if isinstance(value_str, str):
                        processed_values.append(float(value_str.split()[0]))
                    else:
                        processed_values.append(float(value_str))
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Error processing value {v}: {str(e)}")
                    continue
            
            # Process current value
            try:
                if isinstance(current_value, dict):
                    if 'value' in current_value:
                        value_str = current_value['value']
                    elif 'Value' in current_value:
                        value_str = current_value['Value']
                    else:
                        raise ValueError("No valid value field found in dictionary")
                else:
                    value_str = current_value
                
                if isinstance(value_str, str):
                    current_processed = float(value_str.split()[0])
                else:
                    current_processed = float(value_str)
                
                # Combine current and previous values
                all_values = processed_values + [current_processed]
                
                if len(all_values) < 2:
                    logger.warning(f"Insufficient values for trend chart: {len(all_values)}")
                    return None
                
                # Create time points (assuming equal intervals)
                time_points = list(range(len(all_values)))
                
                # Create figure
                fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
                
                # Plot line with gradient color based on trend
                if len(all_values) >= 2:
                    # Determine trend
                    trend = "Stable"
                    if all_values[-1] > all_values[-2]:
                        trend = "Increasing"
                    elif all_values[-1] < all_values[-2]:
                        trend = "Decreasing"
                    
                    # Create gradient line
                    for i in range(len(time_points) - 1):
                        if all_values[i+1] > all_values[i]:
                            color = '#FF9999'  # Red for increasing
                        elif all_values[i+1] < all_values[i]:
                            color = '#99CC99'  # Green for decreasing
                        else:
                            color = '#CCCCCC'  # Gray for stable
                        
                        ax.plot(time_points[i:i+2], all_values[i:i+2], color=color, linewidth=2)
                
                # Add markers
                ax.scatter(time_points[:-1], all_values[:-1], color='#5D9CEC', s=50, zorder=5)
                ax.scatter([time_points[-1]], [all_values[-1]], color='#FF5757', s=80, zorder=5)
                
                # Add value labels
                for i, (x, y) in enumerate(zip(time_points, all_values)):
                    label = f"{y:.1f}"
                    if i == len(time_points) - 1:
                        label += " (Current)"
                    
                    ax.annotate(
                        label,
                        xy=(x, y),
                        xytext=(0, 10),
                        textcoords="offset points",
                        ha='center',
                        fontsize=8
                    )
                
                # Customize chart appearance
                ax.set_title(f'{test_name} Trend', fontsize=12, fontweight='bold')
                ax.set_xticks(time_points)
                ax.set_xticklabels([f"Test {i+1}" for i in range(len(time_points)-1)] + ["Current"])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                plt.tight_layout()
                return fig
                
            except Exception as e:
                logger.error(f"Error processing current value: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating trend chart: {str(e)}")
            return None
    
    def extract_health_score(self, interpretation):
        """Extract health score from interpretation text"""
        try:
            if not interpretation:
                return 0
            
            # Convert interpretation to string if it's a response object
            if hasattr(interpretation, 'text'):
                interpretation_text = interpretation.text
            elif hasattr(interpretation, 'parts'):
                interpretation_text = ''.join([part.text for part in interpretation.parts])
            elif isinstance(interpretation, str):
                interpretation_text = interpretation
            else:
                interpretation_text = str(interpretation)
            
            # Look for patterns like "Health score: 75 (out of 100)"
            for line in interpretation_text.split('\n'):
                if 'score' in line.lower() and '(' in line and ')' in line:
                    score_text = line.split('(')[1].split(')')[0]
                    try:
                        return int(re.search(r'\d+', score_text).group())
                    except:
                        pass
            
            return 0
        except Exception as e:
            logger.error(f"Error extracting health score: {str(e)}")
            return 0