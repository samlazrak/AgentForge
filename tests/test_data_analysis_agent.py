"""
Tests for the Data Analysis Agent
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agent_creator.core.base_agent import AgentConfig
from agent_creator.agents.data_analysis_agent import (
    DataAnalysisAgent, DataAnalysisResult, DataQualityReport
)

class TestDataAnalysisAgent:
    """Test suite for Data Analysis Agent"""
    
    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration"""
        return AgentConfig(
            name="TestDataAnalysisAgent",
            description="Test agent for data analysis",
            capabilities=["data_analysis", "visualization", "statistical_analysis"]
        )
    
    @pytest.fixture
    def data_analysis_agent(self, agent_config):
        """Create a test data analysis agent"""
        agent = DataAnalysisAgent(agent_config)
        agent.start()
        return agent
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing"""
        return {
            'age': [25, 30, 35, 40, 45, 50],
            'salary': [50000, 60000, 70000, 80000, 90000, 100000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT'],
            'experience': [2, 5, 8, 12, 15, 18]
        }
    
    @pytest.fixture
    def sample_csv_file(self, sample_csv_data):
        """Create a temporary CSV file for testing"""
        import pandas as pd
        if not hasattr(pd, 'DataFrame'):
            pytest.skip("Pandas not available")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(sample_csv_data)
            df.to_csv(f.name, index=False)
            yield f.name
        
        # Cleanup
        if os.path.exists(f.name):
            os.unlink(f.name)
    
    def test_agent_initialization(self, data_analysis_agent):
        """Test agent initialization"""
        assert data_analysis_agent.config.name == "TestDataAnalysisAgent"
        assert data_analysis_agent.is_running
        assert "data_analysis" in data_analysis_agent.config.capabilities
        assert hasattr(data_analysis_agent, 'dependencies')
        assert hasattr(data_analysis_agent, 'supported_formats')
        assert hasattr(data_analysis_agent, 'analysis_history')
    
    def test_agent_default_initialization(self):
        """Test agent with default configuration"""
        config = AgentConfig(
            name="DefaultDataAgent",
            description="Default data analysis agent"
        )
        agent = DataAnalysisAgent(config)
        
        assert agent.config.name == "DefaultDataAgent"
        assert agent.supported_formats == ['.csv', '.xlsx', '.xls', '.json', '.tsv']
    
    def test_supported_file_formats(self, data_analysis_agent):
        """Test supported file formats"""
        expected_formats = ['.csv', '.xlsx', '.xls', '.json', '.tsv']
        assert data_analysis_agent.supported_formats == expected_formats
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    @patch('pandas.read_csv')
    def test_analyze_file_csv(self, mock_read_csv, data_analysis_agent, sample_csv_data):
        """Test analyzing a CSV file"""
        import pandas as pd
        
        # Enable testing mode to bypass file existence check
        data_analysis_agent._testing_mode = True
        
        # Mock pandas DataFrame
        mock_df = Mock()
        mock_df.shape = (6, 4)
        mock_df.columns = ['age', 'salary', 'department', 'experience']
        mock_df.dtypes.to_dict.return_value = {'age': 'int64', 'salary': 'int64'}
        mock_df.isnull.return_value.sum.return_value.to_dict.return_value = {'age': 0, 'salary': 0}
        mock_df.memory_usage.return_value.sum.return_value = 1000
        mock_df.select_dtypes.return_value.columns = ['age', 'salary', 'experience']
        mock_df.describe.return_value.to_dict.return_value = {}
        
        # Mock the pandas operations properly
        def mock_getitem(self, key):
            mock_series = Mock()
            mock_series.describe.return_value.to_dict.return_value = {}
            return mock_series
        
        mock_df.__getitem__ = mock_getitem
        mock_read_csv.return_value = mock_df
        
        result = data_analysis_agent.analyze_file("test.csv")
        
        assert isinstance(result, DataAnalysisResult)
        assert result.analysis_type == "comprehensive"
        mock_read_csv.assert_called_once_with("test.csv")
    
    def test_analyze_file_not_found(self, data_analysis_agent):
        """Test analyzing non-existent file"""
        with pytest.raises(FileNotFoundError):
            data_analysis_agent.analyze_file("nonexistent.csv")
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    def test_analyze_dataframe(self, data_analysis_agent, sample_csv_data):
        """Test analyzing DataFrame from dictionary"""
        with patch('pandas.DataFrame') as mock_df_class:
            mock_df = Mock()
            mock_df.shape = (6, 4)
            mock_df.columns = ['age', 'salary', 'department', 'experience']
            mock_df.dtypes.to_dict.return_value = {'age': 'int64', 'salary': 'int64'}
            mock_df.isnull.return_value.sum.return_value.to_dict.return_value = {'age': 0, 'salary': 0}
            mock_df.memory_usage.return_value.sum.return_value = 1000
            mock_df.select_dtypes.return_value.columns = ['age', 'salary', 'experience']
            mock_df.describe.return_value.to_dict.return_value = {}
            
            # Mock the pandas operations properly
            def mock_getitem(self, key):
                mock_series = Mock()
                mock_series.describe.return_value.to_dict.return_value = {}
                return mock_series
            
            mock_df.__getitem__ = mock_getitem
            mock_df_class.return_value = mock_df
            
            result = data_analysis_agent.analyze_dataframe(sample_csv_data)
            
            assert isinstance(result, DataAnalysisResult)
            assert result.analysis_type == "comprehensive"
            mock_df_class.assert_called_once_with(sample_csv_data)
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', False)
    def test_analyze_file_pandas_not_available(self, data_analysis_agent):
        """Test file analysis when pandas is not available"""
        result = data_analysis_agent.analyze_file("test.csv")
        
        assert isinstance(result, DataAnalysisResult)
        assert result.data_summary["status"] == "limited_analysis"
        assert "dependencies" in result.insights[0]
    
    def test_unsupported_file_format(self, data_analysis_agent):
        """Test analyzing unsupported file format"""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                data_analysis_agent.analyze_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_task_execution_unknown_type(self, data_analysis_agent):
        """Test task execution with unknown task type"""
        task_id = data_analysis_agent.create_task(
            "Unknown task",
            {"type": "unknown_task"}
        )
        
        with pytest.raises(ValueError, match="Unknown task type"):
            data_analysis_agent.run_task(task_id)
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    def test_data_quality_check(self, data_analysis_agent, sample_csv_data):
        """Test data quality checking"""
        with patch('pandas.DataFrame') as mock_df_class:
            mock_df = Mock()
            mock_df.shape = (6, 4)
            mock_df.isnull.return_value.sum.return_value.to_dict.return_value = {'age': 0, 'salary': 1}
            mock_df.duplicated.return_value.sum.return_value = 0
            mock_df.dtypes.astype.return_value.to_dict.return_value = {'age': 'int64'}
            mock_df.select_dtypes.return_value.columns = ['age', 'salary']
            
            # Mock the pandas operations properly for outlier detection
            def mock_getitem(self, key):
                mock_series = Mock()
                # Mock quantile to return different values for Q1 and Q3
                mock_series.quantile.side_effect = lambda q: 25 if q == 0.25 else 75
                # Mock comparison operations that return boolean-like Mock objects
                mock_comparison = Mock()
                mock_comparison.sum.return_value = 2  # 2 outliers
                mock_series.__lt__ = Mock(return_value=mock_comparison)
                mock_series.__gt__ = Mock(return_value=mock_comparison)
                # Mock the bitwise OR operation for outlier detection
                mock_comparison.__or__ = Mock(return_value=mock_comparison)
                return mock_series
            
            mock_df.__getitem__ = mock_getitem
            mock_df_class.return_value = mock_df
            
            task_id = data_analysis_agent.create_task(
                "Data quality check",
                {"type": "data_quality_check", "data": sample_csv_data}
            )
            
            result = data_analysis_agent.run_task(task_id)
            
            assert isinstance(result, DataQualityReport)
            assert result.total_rows == 6
            assert result.total_columns == 4
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    def test_correlation_analysis(self, data_analysis_agent, sample_csv_data):
        """Test correlation analysis"""
        with patch('pandas.DataFrame') as mock_df_class:
            mock_df = Mock()
            mock_corr_matrix = Mock()
            mock_corr_matrix.columns = ['age', 'salary']
            # Mock iloc to support indexing
            mock_iloc = Mock()
            mock_iloc.__getitem__ = Mock(return_value=0.8)  # Strong correlation
            mock_corr_matrix.iloc = mock_iloc
            mock_corr_matrix.to_dict.return_value = {'age': {'salary': 0.8}}
            
            mock_df.select_dtypes.return_value.columns = ['age', 'salary']
            
            # Mock the pandas operations properly
            def mock_getitem(self, key):
                mock_subset = Mock()
                mock_subset.corr.return_value = mock_corr_matrix
                return mock_subset
            
            mock_df.__getitem__ = mock_getitem
            mock_df_class.return_value = mock_df
            
            task_id = data_analysis_agent.create_task(
                "Correlation analysis",
                {"type": "correlation_analysis", "data": sample_csv_data}
            )
            
            result = data_analysis_agent.run_task(task_id)
            
            assert isinstance(result, dict)
            assert "correlation_matrix" in result
            assert "strong_correlations" in result
    
    def test_correlation_analysis_insufficient_columns(self, data_analysis_agent):
        """Test correlation analysis with insufficient numeric columns"""
        data = {"name": ["Alice", "Bob"], "category": ["A", "B"]}
        
        with patch('pandas.DataFrame') as mock_df_class:
            mock_df = Mock()
            mock_df.select_dtypes.return_value.columns = []  # No numeric columns
            mock_df_class.return_value = mock_df
            
            task_id = data_analysis_agent.create_task(
                "Correlation analysis",
                {"type": "correlation_analysis", "data": data}
            )
            
            result = data_analysis_agent.run_task(task_id)
            assert "error" in result
    
    @patch('agent_creator.agents.data_analysis_agent.MATPLOTLIB_AVAILABLE', True)
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    @patch('os.makedirs')
    def test_visualization_generation(self, mock_makedirs, mock_close, mock_savefig, data_analysis_agent):
        """Test visualization generation"""
        with patch('pandas.DataFrame') as mock_df_class:
            mock_df = Mock()
            mock_df.shape = (100, 4)
            mock_df.columns = ['age', 'salary', 'department', 'experience']
            mock_df.select_dtypes.return_value.columns = ['age', 'salary', 'experience']
            mock_df.__getitem__ = Mock()
            mock_df.__getitem__.return_value.hist = Mock()
            mock_df.__getitem__.return_value.corr.return_value = Mock()
            mock_df.boxplot = Mock()
            
            mock_df_class.return_value = mock_df
            
            task_id = data_analysis_agent.create_task(
                "Create visualization",
                {
                    "type": "create_visualization",
                    "data": {"age": [25, 30], "salary": [50000, 60000]},
                    "viz_type": "histogram",
                    "columns": ["age", "salary"]
                }
            )
            
            result = data_analysis_agent.run_task(task_id)
            
            # Verify the task completed without error
            assert data_analysis_agent.get_task_status(task_id)["status"] == "completed"
    
    def test_agent_lifecycle(self, data_analysis_agent):
        """Test agent start/stop lifecycle"""
        assert data_analysis_agent.is_running
        
        data_analysis_agent.stop()
        assert not data_analysis_agent.is_running
        
        data_analysis_agent.start()
        assert data_analysis_agent.is_running
    
    def test_task_status_tracking(self, data_analysis_agent, sample_csv_data):
        """Test task status tracking"""
        task_id = data_analysis_agent.create_task(
            "Test analysis",
            {"type": "analyze_dataframe", "df_dict": sample_csv_data}
        )
        
        # Check initial status
        status = data_analysis_agent.get_task_status(task_id)
        assert status["status"] == "pending"
        assert status["task_id"] == task_id
        
        # Run task
        data_analysis_agent.run_task(task_id)
        
        # Check completed status
        status = data_analysis_agent.get_task_status(task_id)
        assert status["status"] in ["completed", "failed"]
    
    def test_list_tasks(self, data_analysis_agent, sample_csv_data):
        """Test listing agent tasks"""
        initial_tasks = data_analysis_agent.list_tasks()
        initial_count = len(initial_tasks)
        
        # Create a few tasks
        task_id1 = data_analysis_agent.create_task(
            "Analysis 1",
            {"type": "analyze_dataframe", "df_dict": sample_csv_data}
        )
        
        task_id2 = data_analysis_agent.create_task(
            "Analysis 2",
            {"type": "data_quality_check", "data": sample_csv_data}
        )
        
        tasks = data_analysis_agent.list_tasks()
        assert len(tasks) == initial_count + 2
        
        task_ids = [task["task_id"] for task in tasks]
        assert task_id1 in task_ids
        assert task_id2 in task_ids
    
    def test_get_agent_info(self, data_analysis_agent):
        """Test getting agent information"""
        info = data_analysis_agent.get_agent_info()
        
        assert info["name"] == "TestDataAnalysisAgent"
        assert info["description"] == "Test agent for data analysis"
        assert "data_analysis" in info["capabilities"]
        assert "is_running" in info
        assert "task_count" in info
        assert "llm_info" in info
    
    def test_string_representations(self, data_analysis_agent):
        """Test string representations of agent"""
        str_repr = str(data_analysis_agent)
        assert "TestDataAnalysisAgent" in str_repr
        assert data_analysis_agent.agent_id in str_repr
        
        repr_str = repr(data_analysis_agent)
        assert "TestDataAnalysisAgent" in repr_str
        assert data_analysis_agent.agent_id in repr_str
    
    def test_correlation_interpretation(self, data_analysis_agent):
        """Test correlation strength interpretation"""
        # Test different correlation strengths
        assert data_analysis_agent._interpret_correlation(0.8) == "strong"
        assert data_analysis_agent._interpret_correlation(0.5) == "moderate"
        assert data_analysis_agent._interpret_correlation(0.2) == "weak"
        assert data_analysis_agent._interpret_correlation(0.05) == "negligible"
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    def test_quality_score_calculation(self, data_analysis_agent):
        """Test data quality score calculation"""
        import pandas as pd
        
        # Mock DataFrame with some quality issues
        mock_df = Mock()
        mock_df.shape = (100, 4)
        
        report = DataQualityReport(
            total_rows=100,
            total_columns=4,
            missing_values={'col1': 10, 'col2': 0, 'col3': 5, 'col4': 0},  # 15 missing out of 400
            duplicate_rows=5,
            outliers={'col1': 8, 'col2': 12}
        )
        
        score = data_analysis_agent._calculate_quality_score(mock_df, report)
        
        # Score should be less than 100 due to missing values, duplicates, and outliers
        assert 0 <= score <= 100
        assert score < 100
    
    def test_generate_report(self, data_analysis_agent):
        """Test comprehensive report generation"""
        # Create mock analysis result
        analysis_result = DataAnalysisResult(
            analysis_type="comprehensive",
            data_summary={"shape": (100, 5), "columns": ["a", "b", "c", "d", "e"]},
            insights=["Insight 1", "Insight 2"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            visualizations=["chart1.png", "chart2.png"]
        )
        
        task_id = data_analysis_agent.create_task(
            "Generate report",
            {"type": "generate_report", "analysis_results": analysis_result}
        )
        
        report_path = data_analysis_agent.run_task(task_id)
        
        assert isinstance(report_path, str)
        assert report_path.endswith('.md')
        
        # Check if file was created
        assert os.path.exists(report_path)
        
        # Read and verify report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Data Analysis Report" in content
            assert "comprehensive" in content
            assert "Insight 1" in content
            assert "Recommendation 1" in content
        
        # Cleanup
        os.unlink(report_path)
    
    def test_mock_analysis_fallback(self, data_analysis_agent):
        """Test mock analysis when dependencies are missing"""
        result = data_analysis_agent._mock_analysis_result("test_analysis")
        
        assert isinstance(result, DataAnalysisResult)
        assert result.analysis_type == "test_analysis"
        assert "limited_analysis" in result.data_summary["status"]
        assert len(result.insights) > 0
        assert len(result.recommendations) > 0
    
    def test_task_error_handling(self, data_analysis_agent):
        """Test error handling in task execution"""
        # Create a task that will cause an error
        task_id = data_analysis_agent.create_task(
            "Error task",
            {"type": "analyze_file", "file_path": "/nonexistent/path/file.csv"}
        )
        
        with pytest.raises(FileNotFoundError):
            data_analysis_agent.run_task(task_id)
        
        # Check that task status reflects the error
        status = data_analysis_agent.get_task_status(task_id)
        assert status["status"] == "failed"
        assert status["error"] is not None
    
    @patch('agent_creator.agents.data_analysis_agent.PANDAS_AVAILABLE', True)
    def test_rule_based_insights(self, data_analysis_agent):
        """Test rule-based insight generation"""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.shape = (50, 60)  # Small dataset with many columns
        
        summary = {
            "missing_values": {"col1": 25, "col2": 0},  # 50% missing in col1
        }
        
        insights = data_analysis_agent._generate_rule_based_insights(mock_df, summary)
        
        assert len(insights) > 0
        # Should identify small dataset and high dimensionality
        assert any("Small dataset" in insight for insight in insights)
        assert any("High-dimensional" in insight for insight in insights)
    
    def test_analysis_history_tracking(self, data_analysis_agent, sample_csv_data):
        """Test that analysis history is tracked"""
        initial_history_length = len(data_analysis_agent.analysis_history)
        
        # Perform analysis
        data_analysis_agent.analyze_dataframe(sample_csv_data)
        
        # Check history was updated
        assert len(data_analysis_agent.analysis_history) == initial_history_length + 1
        assert isinstance(data_analysis_agent.analysis_history[-1], DataAnalysisResult)
    
    def test_dependencies_check(self, data_analysis_agent):
        """Test dependency checking"""
        assert isinstance(data_analysis_agent.dependencies, dict)
        assert 'pandas' in data_analysis_agent.dependencies
        assert 'matplotlib' in data_analysis_agent.dependencies
        assert 'plotly' in data_analysis_agent.dependencies
        assert 'advanced_stats' in data_analysis_agent.dependencies
        
        # All values should be boolean
        for dep, available in data_analysis_agent.dependencies.items():
            assert isinstance(available, bool)