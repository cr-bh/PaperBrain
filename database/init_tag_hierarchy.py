"""
初始化 MECE 标签层级结构
为 AI/OR 研究领域提供结构化的标签分类体系
"""
from database.db_manager import db_manager


def init_tag_hierarchy():
    """初始化标签层级结构"""

    # MECE 标签结构定义
    tag_hierarchy = {
        # 一级：研究领域 (Domain)
        "domain": {
            "Artificial Intelligence": {
                "color": "#3B82F6",
                "children": {
                    "Machine Learning": {"color": "#60A5FA"},
                    "Deep Learning": {"color": "#60A5FA"},
                    "Reinforcement Learning": {"color": "#60A5FA"},
                    "Natural Language Processing": {"color": "#60A5FA"},
                    "Computer Vision": {"color": "#60A5FA"},
                }
            },
            "Operations Research": {
                "color": "#10B981",
                "children": {
                    "Optimization": {"color": "#34D399"},
                    "Scheduling": {"color": "#34D399"},
                    "Resource Allocation": {"color": "#34D399"},
                    "Supply Chain": {"color": "#34D399"},
                }
            },
            "Data Science": {
                "color": "#8B5CF6",
                "children": {
                    "Data Mining": {"color": "#A78BFA"},
                    "Statistical Analysis": {"color": "#A78BFA"},
                    "Predictive Modeling": {"color": "#A78BFA"},
                }
            }
        },

        # 二级：方法论 (Methodology)
        "methodology": {
            "Neural Networks": {
                "color": "#F59E0B",
                "children": {
                    "CNN": {"color": "#FBBF24"},
                    "RNN": {"color": "#FBBF24"},
                    "Transformer": {"color": "#FBBF24"},
                    "GAN": {"color": "#FBBF24"},
                }
            },
            "Optimization Algorithms": {
                "color": "#EF4444",
                "children": {
                    "Genetic Algorithm": {"color": "#F87171"},
                    "Simulated Annealing": {"color": "#F87171"},
                    "Gradient Descent": {"color": "#F87171"},
                }
            },
            "RL Algorithms": {
                "color": "#EC4899",
                "children": {
                    "Q-Learning": {"color": "#F472B6"},
                    "Policy Gradient": {"color": "#F472B6"},
                    "Actor-Critic": {"color": "#F472B6"},
                    "PPO": {"color": "#F472B6"},
                }
            }
        },

        # 三级：应用任务 (Task)
        "task": {
            "Prediction": {
                "color": "#06B6D4",
                "children": {
                    "Time Series Forecasting": {"color": "#22D3EE"},
                    "Demand Prediction": {"color": "#22D3EE"},
                }
            },
            "Classification": {
                "color": "#14B8A6",
                "children": {
                    "Image Classification": {"color": "#2DD4BF"},
                    "Text Classification": {"color": "#2DD4BF"},
                }
            },
            "Generation": {
                "color": "#A855F7",
                "children": {
                    "Text Generation": {"color": "#C084FC"},
                    "Image Generation": {"color": "#C084FC"},
                }
            },
            "Decision Making": {
                "color": "#F97316",
                "children": {
                    "Route Planning": {"color": "#FB923C"},
                    "Resource Scheduling": {"color": "#FB923C"},
                }
            }
        }
    }

    # 创建标签
    created_tags = {}

    for category, parent_tags in tag_hierarchy.items():
        for parent_name, parent_data in parent_tags.items():
            # 创建父标签
            parent_tag = db_manager.create_tag(
                name=parent_name,
                category=category,
                color=parent_data["color"]
            )
            created_tags[parent_name] = parent_tag

            # 创建子标签
            if "children" in parent_data:
                for child_name, child_data in parent_data["children"].items():
                    child_tag = db_manager.create_tag(
                        name=child_name,
                        category=category,
                        parent_id=parent_tag.id,
                        color=child_data["color"]
                    )
                    created_tags[child_name] = child_tag

    print(f"✓ 已创建 {len(created_tags)} 个标签")
    return created_tags


if __name__ == "__main__":
    init_tag_hierarchy()
