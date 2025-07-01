"""
Data Analysis Agent for Agent Creator Framework

Provides comprehensive data analysis capabilities including:
- Data ingestion from CSV, Excel, JSON files
- Statistical analysis and correlation detection
- Automated visualization generation
- Data quality assessment
- Report generation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
import io
import base64

# Data processing imports with fallbacks
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Visualization imports with fallbacks
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.offline import plot
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Statistical analysis imports
try:
    from scipy import stats
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    ADVANCED_STATS_AVAILABLE = True
except ImportError:
    ADVANCED_STATS_AVAILABLE = False

from ..core.base_agent import BaseAgent, AgentTask, AgentConfig

@dataclass
class DataAnalysisResult:
    """Result of data analysis operation"""
    analysis_type: str
    data_summary: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    statistical_tests: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    report_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    total_rows: int
    total_columns: int
    missing_values: Dict[str, int] = field(default_factory=dict)
    duplicate_rows: int = 0
    data_types: Dict[str, str] = field(default_factory=dict)
    outliers: Dict[str, int] = field(default_factory=dict)
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

class DataAnalysisAgent(BaseAgent):
    """
    Agent specialized in data analysis and visualization
    """
    
    def _initialize(self):
        """Initialize data analysis specific components"""
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.tsv', '.atf']
        self.analysis_history = []
        
        # Check dependencies
        self.dependencies = {
            'pandas': PANDAS_AVAILABLE,
            'matplotlib': MATPLOTLIB_AVAILABLE,
            'plotly': PLOTLY_AVAILABLE,
            'advanced_stats': ADVANCED_STATS_AVAILABLE
        }
        
        if not PANDAS_AVAILABLE:
            self.logger.warning("Pandas not available - data analysis will be limited")
            
        self.logger.info(f"Data Analysis Agent initialized with dependencies: {self.dependencies}")
    
    def execute_task(self, task: AgentTask) -> Any:
        """
        Execute data analysis task
        
        Args:
            task: Task to execute
            
        Returns:
            Analysis result
        """
        task_type = task.parameters.get("type")
        
        if task_type == "analyze_file":
            return self._analyze_file(task)
        elif task_type == "analyze_dataframe":
            return self._analyze_dataframe(task)
        elif task_type == "create_visualization":
            return self._create_visualization(task)
        elif task_type == "statistical_analysis":
            return self._statistical_analysis(task)
        elif task_type == "data_quality_check":
            return self._data_quality_check(task)
        elif task_type == "correlation_analysis":
            return self._correlation_analysis(task)
        elif task_type == "generate_report":
            return self._generate_comprehensive_report(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def analyze_file(self, file_path: str, analysis_type: str = "comprehensive") -> DataAnalysisResult:
        """
        Analyze a data file
        
        Args:
            file_path: Path to the data file
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis result
        """
        task_id = self.create_task(
            description=f"Analyze file: {file_path}",
            parameters={
                "type": "analyze_file",
                "file_path": file_path,
                "analysis_type": analysis_type
            }
        )
        return self.run_task(task_id)
    
    def analyze_dataframe(self, df_dict: Dict[str, Any], analysis_type: str = "comprehensive") -> DataAnalysisResult:
        """
        Analyze a DataFrame (passed as dictionary)
        
        Args:
            df_dict: DataFrame data as dictionary
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis result
        """
        task_id = self.create_task(
            description="Analyze DataFrame",
            parameters={
                "type": "analyze_dataframe", 
                "df_dict": df_dict,
                "analysis_type": analysis_type
            }
        )
        return self.run_task(task_id)
    
    def create_visualization(self, data: Union[str, Dict], viz_type: str, columns: List[str] = None) -> str:
        """
        Create a specific visualization
        
        Args:
            data: File path or data dictionary
            viz_type: Type of visualization
            columns: Columns to include
            
        Returns:
            Path to generated visualization
        """
        task_id = self.create_task(
            description=f"Create {viz_type} visualization",
            parameters={
                "type": "create_visualization",
                "data": data,
                "viz_type": viz_type,
                "columns": columns
            }
        )
        return self.run_task(task_id)
    
    def _analyze_file(self, task: AgentTask) -> DataAnalysisResult:
        """Analyze a data file"""
        if not PANDAS_AVAILABLE:
            return self._mock_analysis_result("file_analysis")
        
        file_path = task.parameters["file_path"]
        analysis_type = task.parameters.get("analysis_type", "comprehensive")
        
        # Check file exists (can be bypassed in tests)
        if not hasattr(self, '_testing_mode') and not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load data based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            elif file_ext == '.tsv':
                df = pd.read_csv(file_path, sep='\t')
            elif file_ext == '.atf':
                df = self._parse_atf_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return self._perform_analysis(df, analysis_type, file_path)
            
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def _parse_atf_file(self, file_path: str):
        """Parse ATF (Axon Text Format) file"""
        if not PANDAS_AVAILABLE:
            raise ValueError("Pandas is required for ATF file parsing")
        
        try:
            # ATF files are typically tab-delimited text files with metadata headers
            # First, read the file to identify the structure
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find where the actual data starts (after metadata/header section)
            data_start_idx = 0
            header_line = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Skip ATF version line
                if line.startswith('ATF'):
                    continue
                # Skip dimension line (e.g., "8 2")
                elif line and all(part.isdigit() for part in line.split()):
                    continue
                # Skip comment lines
                elif line.startswith(('!', '#')):
                    continue
                # Look for header line with quotes (column names)
                elif '"' in line:
                    header_line = line
                    continue
                # Check if this is the start of numeric data
                elif line and any(char.isdigit() or char in '.-' for char in line.split('\t')[0]):
                    data_start_idx = i
                    break
            
            # Read the data portion starting from data_start_idx
            if data_start_idx < len(lines):
                # Write the data portion to a temporary file for pandas to read
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp_file:
                    # If we found a header line, use it for column names
                    if header_line:
                        # Clean up header line - remove quotes and use as first line
                        clean_header = header_line.replace('"', '')
                        tmp_file.write(clean_header + '\n')
                    
                    # Write data lines
                    tmp_file.writelines(lines[data_start_idx:])
                    tmp_file_path = tmp_file.name
                
                try:
                    # Try to read as tab-separated values
                    df = pd.read_csv(tmp_file_path, sep='\t', encoding='utf-8')
                except:
                    # Fallback: try comma-separated
                    df = pd.read_csv(tmp_file_path, encoding='utf-8')
                finally:
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                
                # Add metadata to DataFrame attributes if possible
                metadata = {}
                for line in lines[:data_start_idx]:
                    line = line.strip()
                    if line and not line.startswith(('ATF', '#', '!')):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        metadata[key.strip().lstrip('#!')] = value.strip()
                
                # Store metadata as DataFrame attribute
                if hasattr(df, 'attrs'):
                    df.attrs.update(metadata)
                
                self.logger.info(f"Successfully parsed ATF file: {df.shape[0]} rows, {df.shape[1]} columns")
                return df
            else:
                raise ValueError("No data found in ATF file")
                
        except Exception as e:
            self.logger.error(f"Error parsing ATF file {file_path}: {e}")
            # Fallback: try reading as regular TSV
            try:
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                self.logger.warning(f"ATF file parsed as simple TSV: {df.shape[0]} rows, {df.shape[1]} columns")
                return df
            except:
                raise ValueError(f"Unable to parse ATF file: {e}")
    
    def _analyze_dataframe(self, task: AgentTask) -> DataAnalysisResult:
        """Analyze a DataFrame from dictionary"""
        if not PANDAS_AVAILABLE:
            return self._mock_analysis_result("dataframe_analysis")
        
        df_dict = task.parameters["df_dict"]
        analysis_type = task.parameters.get("analysis_type", "comprehensive")
        
        try:
            df = pd.DataFrame(df_dict)
            return self._perform_analysis(df, analysis_type)
            
        except Exception as e:
            self.logger.error(f"Error creating DataFrame: {e}")
            raise
    
    def _perform_analysis(self, df, analysis_type: str, source_file: str = None) -> DataAnalysisResult:
        """Perform comprehensive data analysis"""
        result = DataAnalysisResult(analysis_type=analysis_type)
        
        # Basic data summary
        result.data_summary = self._get_basic_summary(df)
        
        # Generate visualizations
        if MATPLOTLIB_AVAILABLE or PLOTLY_AVAILABLE:
            result.visualizations = self._generate_visualizations(df, source_file)
        
        # Statistical analysis
        if analysis_type in ["comprehensive", "statistical"]:
            result.statistical_tests = self._perform_statistical_tests(df)
        
        # Generate insights using LLM
        result.insights = self._generate_insights(df, result.data_summary, result.statistical_tests)
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(df, result.data_summary)
        
        # Store in history
        self.analysis_history.append(result)
        
        return result
    
    def _get_basic_summary(self, df) -> Dict[str, Any]:
        """Get basic data summary statistics"""
        if not PANDAS_AVAILABLE:
            return {}
        
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
        }
        
        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
        
        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary["categorical_summary"] = {}
            for col in categorical_cols:
                summary["categorical_summary"][col] = {
                    "unique_values": df[col].nunique(),
                    "most_common": df[col].value_counts().head().to_dict()
                }
        
        return summary
    
    def _generate_visualizations(self, df, source_file: str = None) -> List[str]:
        """Generate automatic visualizations"""
        visualizations = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not MATPLOTLIB_AVAILABLE and not PLOTLY_AVAILABLE:
            return visualizations
        
        try:
            # Create visualizations directory
            viz_dir = "visualizations"
            os.makedirs(viz_dir, exist_ok=True)
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            # Distribution plots for numeric columns
            if len(numeric_cols) > 0 and MATPLOTLIB_AVAILABLE:
                self._create_distribution_plots(df, numeric_cols, viz_dir, timestamp)
                visualizations.append(f"{viz_dir}/distributions_{timestamp}.png")
            
            # Correlation heatmap
            if len(numeric_cols) > 1 and MATPLOTLIB_AVAILABLE:
                self._create_correlation_heatmap(df, numeric_cols, viz_dir, timestamp)
                visualizations.append(f"{viz_dir}/correlation_{timestamp}.png")
            
            # Box plots for outlier detection
            if len(numeric_cols) > 0 and MATPLOTLIB_AVAILABLE:
                self._create_box_plots(df, numeric_cols, viz_dir, timestamp)
                visualizations.append(f"{viz_dir}/boxplots_{timestamp}.png")
            
            # Categorical analysis
            if len(categorical_cols) > 0 and MATPLOTLIB_AVAILABLE:
                self._create_categorical_plots(df, categorical_cols, viz_dir, timestamp)
                visualizations.append(f"{viz_dir}/categorical_{timestamp}.png")
                
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {e}")
        
        return visualizations
    
    def _create_distribution_plots(self, df, numeric_cols, viz_dir: str, timestamp: str):
        """Create distribution plots for numeric columns"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        n_cols = min(len(numeric_cols), 4)
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols[:16]):  # Limit to 16 columns
            df[col].hist(bins=30, ax=axes[i], alpha=0.7)
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/distributions_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_correlation_heatmap(self, df, numeric_cols, viz_dir: str, timestamp: str):
        """Create correlation heatmap"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        plt.figure(figsize=(12, 10))
        correlation_matrix = df[numeric_cols].corr()
        
        if MATPLOTLIB_AVAILABLE:
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, fmt='.2f')
        else:
            plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
            plt.colorbar()
        
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/correlation_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_box_plots(self, df, numeric_cols, viz_dir: str, timestamp: str):
        """Create box plots for outlier detection"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        n_cols = min(len(numeric_cols), 4)
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols[:16]):
            df.boxplot(column=col, ax=axes[i])
            axes[i].set_title(f'Box Plot of {col}')
        
        # Hide unused subplots
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/boxplots_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_categorical_plots(self, df, categorical_cols, viz_dir: str, timestamp: str):
        """Create plots for categorical data"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        n_cols = min(len(categorical_cols), 2)
        n_rows = (len(categorical_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 6*n_rows))
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(categorical_cols[:8]):  # Limit to 8 columns
            top_values = df[col].value_counts().head(10)
            top_values.plot(kind='bar', ax=axes[i])
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Count')
            axes[i].tick_params(axis='x', rotation=45)
        
        # Hide unused subplots
        for i in range(len(categorical_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/categorical_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _perform_statistical_tests(self, df) -> Dict[str, Any]:
        """Perform statistical tests on the data"""
        if not PANDAS_AVAILABLE:
            return {}
        
        tests = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Normality tests
        if len(numeric_cols) > 0 and ADVANCED_STATS_AVAILABLE:
            normality_tests = {}
            for col in numeric_cols:
                if df[col].notna().sum() > 8:  # Need at least 8 samples for test
                    try:
                        statistic, p_value = stats.shapiro(df[col].dropna())
                        normality_tests[col] = {
                            "statistic": float(statistic),
                            "p_value": float(p_value),
                            "is_normal": bool(p_value > 0.05)
                        }
                    except Exception:
                        pass
            tests["normality"] = normality_tests
        
        # Correlation significance tests
        if len(numeric_cols) > 1:
            correlation_tests = {}
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    try:
                        corr_coef = df[col1].corr(df[col2])
                        if not np.isnan(corr_coef):
                            correlation_tests[f"{col1}_vs_{col2}"] = {
                                "correlation": float(corr_coef),
                                "strength": self._interpret_correlation(abs(corr_coef))
                            }
                    except Exception:
                        pass
            tests["correlations"] = correlation_tests
        
        return tests
    
    def _interpret_correlation(self, corr_value: float) -> str:
        """Interpret correlation strength"""
        if corr_value >= 0.7:
            return "strong"
        elif corr_value >= 0.3:
            return "moderate"
        elif corr_value >= 0.1:
            return "weak"
        else:
            return "negligible"
    
    def _generate_insights(self, df, summary: Dict, statistical_tests: Dict) -> List[str]:
        """Generate insights using LLM"""
        insights = []
        
        # Create a comprehensive data description for the LLM
        data_description = self._create_data_description(df, summary, statistical_tests)
        
        # Use LLM to generate insights
        if self.llm.is_model_loaded():
            prompt = f"""
            Analyze the following dataset and provide key insights:
            
            {data_description}
            
            Please provide 3-5 key insights about this data, focusing on:
            1. Notable patterns or trends
            2. Data quality observations
            3. Interesting correlations or relationships
            4. Potential business implications
            5. Recommendations for further analysis
            
            Format as a numbered list.
            """
            
            try:
                response = self.llm.generate_response(prompt)
                # Parse response into individual insights
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Clean up the line
                        insight = line.lstrip('0123456789.-• ').strip()
                        if insight:
                            insights.append(insight)
            except Exception as e:
                self.logger.error(f"Error generating LLM insights: {e}")
        
        # Add rule-based insights as fallback
        insights.extend(self._generate_rule_based_insights(df, summary))
        
        return insights[:8]  # Limit to 8 insights
    
    def _create_data_description(self, df, summary: Dict, statistical_tests: Dict) -> str:
        """Create a description of the data for LLM analysis"""
        desc_parts = []
        
        # Basic info
        desc_parts.append(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Column types
        if "dtypes" in summary:
            numeric_count = sum(1 for dtype in summary["dtypes"].values() if 'int' in str(dtype) or 'float' in str(dtype))
            text_count = sum(1 for dtype in summary["dtypes"].values() if 'object' in str(dtype))
            desc_parts.append(f"Column types: {numeric_count} numeric, {text_count} text/categorical")
        
        # Missing values
        if "missing_values" in summary:
            total_missing = sum(summary["missing_values"].values())
            if total_missing > 0:
                desc_parts.append(f"Missing values: {total_missing} total missing values")
        
        # Numeric summary highlights
        if "numeric_summary" in summary:
            for col, stats in summary["numeric_summary"].items():
                if isinstance(stats, dict) and "mean" in stats:
                    desc_parts.append(f"{col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
        
        # Correlation highlights
        if "correlations" in statistical_tests:
            strong_corrs = [(k, v) for k, v in statistical_tests["correlations"].items() 
                          if v.get("strength") in ["strong", "moderate"]]
            if strong_corrs:
                desc_parts.append(f"Notable correlations: {len(strong_corrs)} significant correlations found")
        
        return " | ".join(desc_parts)
    
    def _generate_rule_based_insights(self, df, summary: Dict) -> List[str]:
        """Generate insights using rule-based analysis"""
        insights = []
        
        # Missing data insights
        if "missing_values" in summary:
            total_missing = sum(summary["missing_values"].values())
            if total_missing > 0:
                missing_percentage = (total_missing / (df.shape[0] * df.shape[1])) * 100
                insights.append(f"Dataset has {missing_percentage:.1f}% missing values, consider data cleaning")
        
        # Data size insights
        rows, cols = df.shape
        if rows < 100:
            insights.append("Small dataset - consider collecting more data for robust analysis")
        elif rows > 100000:
            insights.append("Large dataset - excellent for machine learning and statistical analysis")
        
        # Column diversity insights
        if cols > 50:
            insights.append("High-dimensional dataset - consider dimensionality reduction techniques")
        
        return insights
    
    def _generate_recommendations(self, df, summary: Dict) -> List[str]:
        """Generate analysis recommendations"""
        recommendations = []
        
        # Data quality recommendations
        if "missing_values" in summary:
            high_missing_cols = [col for col, missing in summary["missing_values"].items() 
                               if missing > df.shape[0] * 0.1]
            if high_missing_cols:
                recommendations.append(f"Consider dropping or imputing columns with high missing values: {', '.join(high_missing_cols[:3])}")
        
        # Analysis recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            recommendations.append("Perform correlation analysis to identify relationships between variables")
        
        if len(numeric_cols) > 3:
            recommendations.append("Consider Principal Component Analysis (PCA) for dimensionality reduction")
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            recommendations.append("Analyze categorical variables for potential feature engineering opportunities")
        
        return recommendations
    
    def _data_quality_check(self, task: AgentTask) -> DataQualityReport:
        """Perform comprehensive data quality check"""
        if not PANDAS_AVAILABLE:
            return DataQualityReport(total_rows=0, total_columns=0)
        
        df_source = task.parameters.get("data")
        if isinstance(df_source, str):
            # File path
            df = pd.read_csv(df_source)  # Simplified for demo
        else:
            # DataFrame dict
            df = pd.DataFrame(df_source)
        
        report = DataQualityReport(
            total_rows=df.shape[0],
            total_columns=df.shape[1]
        )
        
        # Missing values analysis
        report.missing_values = df.isnull().sum().to_dict()
        
        # Duplicate rows
        report.duplicate_rows = df.duplicated().sum()
        
        # Data types
        report.data_types = df.dtypes.astype(str).to_dict()
        
        # Outlier detection for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            report.outliers[col] = int(outliers)
        
        # Calculate quality score
        report.quality_score = self._calculate_quality_score(df, report)
        
        # Generate issues and suggestions
        report.issues, report.suggestions = self._analyze_quality_issues(df, report)
        
        return report
    
    def _calculate_quality_score(self, df, report: DataQualityReport) -> float:
        """Calculate overall data quality score (0-100)"""
        score = 100.0
        
        # Deduct for missing values
        missing_percentage = sum(report.missing_values.values()) / (df.shape[0] * df.shape[1])
        score -= missing_percentage * 30
        
        # Deduct for duplicates
        duplicate_percentage = report.duplicate_rows / df.shape[0] if df.shape[0] > 0 else 0
        score -= duplicate_percentage * 20
        
        # Deduct for high outlier ratio
        if report.outliers:
            avg_outlier_ratio = sum(report.outliers.values()) / (len(report.outliers) * df.shape[0])
            score -= avg_outlier_ratio * 15
        
        return max(0.0, score)
    
    def _analyze_quality_issues(self, df, report: DataQualityReport) -> tuple:
        """Analyze quality issues and generate suggestions"""
        issues = []
        suggestions = []
        
        # Missing values issues
        high_missing = [col for col, missing in report.missing_values.items() 
                       if missing > df.shape[0] * 0.2]
        if high_missing:
            issues.append(f"High missing values in columns: {', '.join(high_missing)}")
            suggestions.append("Consider imputation or dropping columns with >20% missing values")
        
        # Duplicate issues  
        if report.duplicate_rows > 0:
            issues.append(f"{report.duplicate_rows} duplicate rows found")
            suggestions.append("Remove duplicate rows to improve data quality")
        
        # Outlier issues
        high_outlier_cols = [col for col, outliers in report.outliers.items() 
                           if outliers > df.shape[0] * 0.05]
        if high_outlier_cols:
            issues.append(f"High outlier count in: {', '.join(high_outlier_cols)}")
            suggestions.append("Investigate outliers - they may indicate data errors or interesting patterns")
        
        return issues, suggestions
    
    def _correlation_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Perform detailed correlation analysis"""
        if not PANDAS_AVAILABLE:
            return {"error": "Pandas not available"}
        
        df_source = task.parameters.get("data")
        if isinstance(df_source, str):
            df = pd.read_csv(df_source)
        else:
            df = pd.DataFrame(df_source)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation analysis"}
        
        correlation_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Strong correlation threshold
                    strong_correlations.append({
                        "variable1": correlation_matrix.columns[i],
                        "variable2": correlation_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": self._interpret_correlation(abs(corr_value))
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "summary": f"Found {len(strong_correlations)} strong correlations"
        }
    
    def _create_visualization(self, task: AgentTask) -> str:
        """Create a specific visualization"""
        if not PANDAS_AVAILABLE:
            return "Visualization creation requires pandas"
        
        data = task.parameters.get("data")
        viz_type = task.parameters.get("viz_type", "histogram")
        columns = task.parameters.get("columns")
        
        # Load data
        if isinstance(data, str):
            # File path
            if data.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(data)
            else:
                return "Unsupported file format for visualization"
        else:
            # Data dictionary
            import pandas as pd
            df = pd.DataFrame(data)
        
        # Generate visualization based on type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_path = f"visualization_{viz_type}_{timestamp}.png"
        
        if MATPLOTLIB_AVAILABLE:
            self._create_specific_visualization(df, viz_type, columns or [], viz_path)
        
        return viz_path
    
    def _create_specific_visualization(self, df, viz_type: str, columns: List[str], output_path: str):
        """Create specific type of visualization"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        import matplotlib.pyplot as plt
        
        try:
            plt.figure(figsize=(10, 6))
            
            if viz_type == "histogram":
                if columns:
                    for col in columns:
                        if col in df.columns:
                            df[col].hist(alpha=0.7, label=col)
                    plt.legend()
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        df[numeric_cols[0]].hist()
                plt.title("Histogram")
                
            elif viz_type == "scatter":
                if columns and len(columns) >= 2:
                    plt.scatter(df[columns[0]], df[columns[1]])
                    plt.xlabel(columns[0])
                    plt.ylabel(columns[1])
                plt.title("Scatter Plot")
                
            elif viz_type == "line":
                if columns:
                    for col in columns:
                        if col in df.columns:
                            plt.plot(df[col], label=col)
                    plt.legend()
                plt.title("Line Plot")
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
    
    def _statistical_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Perform statistical analysis"""
        if not PANDAS_AVAILABLE:
            return {"error": "Pandas not available for statistical analysis"}
        
        data = task.parameters.get("data")
        
        if isinstance(data, str):
            # File path
            import pandas as pd
            df = pd.read_csv(data)
        else:
            # Data dictionary
            import pandas as pd
            df = pd.DataFrame(data)
        
        return self._perform_statistical_tests(df)

    def _generate_comprehensive_report(self, task: AgentTask) -> str:
        """Generate a comprehensive analysis report"""
        analysis_results = task.parameters.get("analysis_results")
        if not analysis_results:
            raise ValueError("No analysis results provided for report generation")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"data_analysis_report_{timestamp}.md"
        
        # Generate report content
        report_content = self._create_report_content(analysis_results)
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Generated comprehensive report: {report_path}")
        return report_path
    
    def _create_report_content(self, results: DataAnalysisResult) -> str:
        """Create formatted report content"""
        content = f"""# Data Analysis Report

**Generated:** {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type:** {results.analysis_type}

## Executive Summary

This report presents a comprehensive analysis of the provided dataset, including statistical summaries, visualizations, and actionable insights.

## Dataset Overview

- **Shape:** {results.data_summary.get('shape', 'N/A')}
- **Columns:** {len(results.data_summary.get('columns', []))}
- **Memory Usage:** {results.data_summary.get('memory_usage', 'N/A')} bytes

## Key Insights

"""
        
        for i, insight in enumerate(results.insights, 1):
            content += f"{i}. {insight}\n"
        
        content += "\n## Statistical Analysis\n\n"
        
        if results.statistical_tests:
            for test_type, test_results in results.statistical_tests.items():
                content += f"### {test_type.title()} Tests\n\n"
                if isinstance(test_results, dict):
                    for key, value in test_results.items():
                        content += f"- **{key}:** {value}\n"
                content += "\n"
        
        content += "## Recommendations\n\n"
        
        for i, recommendation in enumerate(results.recommendations, 1):
            content += f"{i}. {recommendation}\n"
        
        if results.visualizations:
            content += "\n## Generated Visualizations\n\n"
            for viz_path in results.visualizations:
                content += f"- {viz_path}\n"
        
        return content
    
    def _mock_analysis_result(self, analysis_type: str) -> DataAnalysisResult:
        """Generate mock analysis result when dependencies are missing"""
        return DataAnalysisResult(
            analysis_type=analysis_type,
            data_summary={
                "status": "limited_analysis",
                "reason": "Required dependencies (pandas, matplotlib) not available"
            },
            insights=[
                "Analysis limited due to missing dependencies",
                "Install pandas and matplotlib for full functionality",
                "Mock data analysis performed"
            ],
            recommendations=[
                "Install required packages: pip install pandas matplotlib seaborn",
                "Re-run analysis after installing dependencies"
            ]
        )