import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
import streamlit as st
# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
st.set_page_config(
    page_title="无畏契约信息管理系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 定义主题色彩 - 优化了文字与背景的对比度
COLORS = {
    "primary": "#FF4655",  # 无畏契约主色调
    "secondary": "#1A1A2E",
    "accent": "#00FFFF",
    "background": "#0F1923",
    "card_bg": "#1A2233",
    "text": "#FFFFFF",  # 保持白色主文本以确保最大对比度
    "text_secondary": "#E0E0E0",  # 提高次要文字亮度，从#AAAAAA改为#E0E0E0
    "header": "#FFFFFF",  # 标题也使用纯白以提高可读性
    "success": "#66BB6A",  # 稍微提亮成功颜色
    "warning": "#FFCA28",  # 稍微提亮警告颜色
    "danger": "#EF5350"    # 保持危险颜色
}

# 定位对应的图标和颜色
POSITION_ICONS = {
    "先锋": "🛡️",
    "决斗": "⚔️",
    "控场": "🌫️",
    "哨位": "🔍"
}

POSITION_COLORS = {
    "先锋": "#5C6BC0",
    "决斗": "#EF5350",
    "控场": "#AB47BC",
    "哨位": "#43A047"
}

# 难度对应的图标和颜色
DIFFICULTY_ICONS = {
    "低": "🌱",
    "中": "🏆",
    "高": "💎"
}

DIFFICULTY_COLORS = {
    "低": "#4CAF50",
    "中": "#FFC107",
    "高": "#F44336"
}

class ValorantInfoSystem:
    def __init__(self):
        """初始化无畏契约信息管理系统"""
        # 初始化英雄数据
        self.heroes_data = self._load_heroes_data()
        # 初始化武器数据
        self.weapons_data = self._load_weapons_data()

    def _load_heroes_data(self) -> pd.DataFrame:
        """从提供的数据中加载英雄信息"""
        # 创建英雄数据字典
        heroes_list = []

        # 从提供的文本数据中提取英雄信息
        heroes_data_text = """
先锋	钛狐	Q 沉默爬虫；C 震荡脉冲；E 闪光信标；X 全息诱饵	低	常规脚步声，无特殊标识，辨识度低	E 技能闪光释放无延迟，Q 技能爬虫行进速度均匀，适合快速探查角落
先锋	铁臂	Q 爆破炮弹穿墙伤害；C 致盲弹；E 蓄力冲击震荡；X 震波炸药击飞	中	沉重沉闷的机械音，辨识度极高	C 技能致盲弹爆炸延迟 2.2 秒；X 技能释放后瞬间对路径敌人生效，蓄力技能需把控距离
先锋	猎枭	Q 雷击箭范围伤害；C 无人机标记；E 侦查箭探测；X 连锁雷击	低	常规脚步声，无特殊音效	E 技能侦查箭 5.6 秒内每隔 1.9 秒探测一次；C 技能无人机持续 10 秒，被攻击有明确命中音效
先锋	斯凯	Q 飞鹰闪光；C 突进宠物震荡；E 治愈队友；X 追踪灵体降视野	低	与奎泽脚步声相近，无特殊音效	E 技能治愈可反复使用无延迟；Q 技能飞鹰激活闪光无延迟，上手门槛低
先锋	K/O	Q 闪光弹；C 手雷；E 侦查扫描；X 无效命令压制技能	中	机械感极强的液压腿声，关节处有额外轴承摩擦音	X 技能释放无延迟，持续 10 秒压制敌人技能；E 技能扫描瞬间完成标记
先锋	黑梦	Q 致盲技能；C 揭示敌人位置；E 致聋效果；X 噩梦领域	低	金属部件碰撞叮当声，声音较小	C 技能揭示敌人位置无延迟，E 技能致聋效果持续时间短，操作无需复杂配合
先锋	盖可	Q 闪光道具反复侦查；C 皮蛋干扰；E 束缚鲨鲨；X 拆包辅助	低	与列潇脚步声归为一组，无特殊标识	C 技能皮蛋可反复回收，释放无延迟；X 技能辅助拆包时干扰敌人无延迟
决斗	捷风	Q 拖拽烟雾弹；C 腾空滑翔；E 突进；X 可填充飞刀	中	运动裤摩擦的清脆音效	E 技能突进释放瞬间完成，击杀两人自动充能；Q 技能烟雾拖拽无延迟
决斗	雷兹	Q 爆炸机器人；C 炸药包位移；E 二次爆炸手雷；X 火箭发射器	中	无特殊音效，脚步声常规	C 技能炸药包引爆无延迟，自身会被击飞；X 技能火箭接触实体即爆炸，无飞行延迟
决斗	不死鸟	Q 火焰伤害；C 自我恢复；E 闪光突破；X 击倒复活	中	与炼狱、壹决脚步声归为一组	E 技能闪光是快速突破型，释放无延迟；X 技能倒地后复活触发时间短，容错率高
决斗	芮娜	Q 致盲；C 噬魂回复；E 睥睨单挑；X 隐身加速	中	高跟鞋清脆响声，辨识度高	释放 E 技能闪光曲球后武器切换延迟 0.6 秒；C 技能噬魂击杀后瞬间回复血量
决斗	夜露	Q 反弹闪光；C 分身致盲；E 锚索传送；X 隐身位面	高	与壹决、不死鸟归为一组，可通过分身制造虚假脚步声	E 技能锚索放置后可持续 30 秒，传送无延迟；Q 技能闪光触发延迟短，需精准反弹
决斗	霓虹	Q 闪电弹球；C 高速奔跑；E 滑行；X 闪电光束	中	常规脚步声，无特殊标识	释放 Q 技能后武器切换延迟 1 秒；C 技能奔跑激活瞬间提速，适合快速突破
决斗	壹决	Q 能量墙挡子弹；C 能量剑抑制；E 护盾；X 单挑决斗场	中	与夜露、不死鸟脚步声相近	Q 技能能量墙释放瞬间生成；E 技能护盾触发无延迟，抵挡一次远程伤害
控场	幽影	Q 致盲道具；C 传送；E 球形烟雾；X 隐身突袭	中	无特殊音效，脚步声常规	C 技能传送吟唱时间短，约 0.5 秒；E 技能球形烟雾激活无延迟，可快速封视野
控场	炼狱	Q 燃烧榴弹；C 加速图腾；E 球形烟雾；X 大范围伤害	中	脚步声沉重，带有重甲碰撞音	E 技能烟雾释放后 0.75 秒落下，持续 14.25 秒；C 技能加速图腾持续 12 秒
控场	蝰蛇	Q 毒区易伤；C 可开关烟雾；E 烟雾喷射器；X 毒雾领域	中	常规脚步声，无特殊标识	C 和 E 技能烟雾激活释放约 0.5 秒；X 技能毒雾持续伤害，最低将敌人血量压至 1 点
控场	星燧	Q 引力陷阱易伤；C 震荡星体；E 烟雾星体；X 声音阻隔裂隙	高	无特殊音效，脚步声常规	Q 技能启动时间 1.25 秒；X 技能生成裂隙需选定两点，21 秒内完全阻隔声音和子弹
控场	海神	Q 水形烟雾；C 水流减速；E 护盾；X 巨浪冲击	中	脚步声沉重，带有水流晃动音	Q 技能水形烟雾激活无延迟；E 技能护盾生成瞬间完成，可辅助队友推进
控场	暮蝶	Q 虹吸回复；C 阵亡封烟；E 烟雾；X 复活自身	低	运动鞋脚步声，无特殊标识	C 技能阵亡后自动封烟，无需手动操作；X 技能复活触发时间短，残局容错率高
哨位	贤者	Q 治疗队友；C 冰墙；E 减速区域；X 复活队友	低	草鞋摩擦的沙沙声，脚步声最轻	Q 技能治疗持续生效，无释放延迟；X 技能复活队友释放时间约 2 秒，需持续瞄准
哨位	零	Q 数码囚牢；C 隐形绊线；E 监控标记；X 获取敌方位置	低	镶金属片的皮鞋声，金属音效明显	E 技能监控部署瞬间完成；C 技能绊线触发无延迟
哨位	奇乐	Q 隐形手雷；C 隐身无人机；E 自动炮台；X 禁锢装置	低	类似小鸡摆动的特殊音效	E 技能炮台部署后瞬间锁定敌人；X 技能禁锢装置蓄力完成后无延迟生效
哨位	尚勃勒	Q 扫描陷阱减速；C 重型手枪；E 锚点传送；X 秒杀狙击枪	中	低沉的高贵皮靴声	E 技能锚点传送瞬间完成；X 技能狙击枪装备释放时间约 1 秒
哨位	钢锁	Q 重力捕网束缚；C 窃听器；E 震荡装置；X 大范围束缚	低	与欧盟脚步声相近，无特殊标识	Q 技能捕网释放无延迟，触发束缚效果快；C 窃听器部署瞬间完成监听
哨位	维斯	Q 闪光回收；C 阻隔墙；E 棘刺陷阱；X 缴械技能	低	无特殊音效，脚步声常规	Q 技能闪光可反复回收，释放无延迟；X 技能缴械释放瞬间生效，压制敌人进攻
        """.strip().split('\n')

        # 解析每行数据
        for line in heroes_data_text:
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 5:
                # 提取各个字段
                position = parts[0]
                hero_name = parts[1]
                skills = parts[2]
                difficulty = parts[3]
                footsteps = parts[4]
                skill_time = parts[5] if len(parts) > 5 else ""

                # 解析技能信息
                skills_dict = {}
                for skill in skills.split('；'):
                    if ' ' in skill:
                        skill_code, skill_desc = skill.split(' ', 1)
                        skills_dict[skill_code] = skill_desc

                heroes_list.append({
                    'position': position,
                    'hero_name': hero_name,
                    'skills': skills,
                    'skills_dict': skills_dict,
                    'difficulty': difficulty,
                    'footsteps': footsteps,
                    'skill_time': skill_time,
                    'position_icon': POSITION_ICONS.get(position, "🎮"),
                    'difficulty_icon': DIFFICULTY_ICONS.get(difficulty, "⭐"),
                    'position_color': POSITION_COLORS.get(position, COLORS["primary"]),
                    'difficulty_color': DIFFICULTY_COLORS.get(difficulty, COLORS["primary"])
                })

        return pd.DataFrame(heroes_list)

    def _load_weapons_data(self) -> pd.DataFrame:
        """从提供的数据中加载武器信息"""
        weapons_list = []

        # 从提供的文本数据中提取武器信息
        weapons_data_text = """
手枪	标配	1.75 秒	无开镜功能	0.2 秒	利：免费初始武器，辅助攻击霰弹近距离强势；弊：远距离伤害极低，打腿需 8 枪才可击杀
手枪	短炮	2 秒	无开镜功能	0.2 秒	利：售价仅 150，半自动模式近距离容错率高；弊：穿透力低，中距离伤害骤降
手枪	狂怒	1.75 秒	无开镜功能	0.2 秒	利：全自动模式，近距离泼水输出强；弊：弹夹容量小，中远距离需点射，容错率低
手枪	鬼魅	1.5 秒	无开镜功能	0.2 秒	利：带消音器，精准度高，爆头两发击杀；弊：半自动模式，依赖枪法，中距离对枪弱势
手枪	正义	2.25 秒	无开镜功能	0.3 秒	利：30 米内爆头一枪击杀，eco 局性价比高；弊：后坐力最大，后坐力恢复时间长，出枪慢
冲锋枪	蜂刺	2 秒	无开镜功能	0.3 秒	利：价格低，近距离射速快；弊：精准度低，弹夹容量小，中远距离伤害衰减严重
冲锋枪	骇灵	2.2 秒	无开镜功能	0.3 秒	利：带消音器，穿透力强，弹夹容量大；弊：单发伤害低，远距离输出效率差
霰弹枪	雄鹿	2.5 秒	无开镜功能	0.4 秒	利：有空爆模式，中距离杀伤力强；弊：近距离伤害不如其他霰弹枪，射速慢
霰弹枪	判官	2.2 秒	无开镜功能	0.4 秒	利：全自动模式，中等穿透力，近距离压制强；弊：价格 1850 偏高，远距离基本无伤害
步枪	獠犬	2.2 秒	三连发模式开镜，后坐力降低	0.3 秒	利：价格低，三连发模式精准度高；弊：弹夹仅 24 发，连射后坐力偏移明显
步枪	戍卫	2.5 秒	1.5 倍开镜，开镜瞬间完成	0.3 秒	利：单发伤害最高，远距离点射强势；弊：半自动模式，近距离遭遇战容错率低
步枪	幻影	2.5 秒	1.25 倍镜，开镜后后坐力降低	0.3 秒	利：弹道散射小，枪声低，适合蹲点防守；弊：远距离伤害衰减，打腿需 6 枪击杀
步枪	狂徒	2.5 秒	1.25 倍镜，开镜无延迟	0.3 秒	利：单发伤害高，爆头一击致命；弊：后坐力大，横移射击时精准度下降明显
狙击枪	飞将	3.0 秒	1.5 倍开镜，开镜速度快	0.5 秒	利：价格仅 950，射速比冥驹快一倍；弊：伤害不足，远距离需两枪击杀
狙击枪	莽侠	3.5 秒	1.5 倍开镜，支持两连发	0.6 秒	利：中距离两连发可快速击杀；弊：装弹时间长，空枪后易被反制
狙击枪	冥驹	3.7 秒	2.5 倍和 5 倍双开镜模式	1.5 秒	利：单发伤害最高，任意距离击中即重创；弊：价格 4700 偏高，射速极低，灵活性差
机关枪	战神	4 秒	开镜后后坐力降低	0.8 秒	利：弹夹容量大，持续压制能力强；弊：机动性差，换弹时间长，近距离转向慢
机关枪	奥丁	5 秒	开镜后精准度提升	1 秒	利：弹夹容量是战神两倍，杀伤力更高；弊：价格高，机动性极差，换弹期间易被偷袭
近战武器	军刀	无换弹时间	无开镜功能	0.1 秒	利：手持移速最快，背刺一击必杀；弊：攻击距离极短，正面作战毫无优势
        """.strip().split('\n')

        # 武器类型对应的图标
        weapon_type_icons = {
            "手枪": "🔫",
            "冲锋枪": "💨",
            "霰弹枪": "💥",
            "步枪": "🔫",
            "狙击枪": "🎯",
            "机关枪": "🔥",
            "近战武器": "🗡️"
        }

        # 解析每行数据
        for line in weapons_data_text:
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 6:
                weapon_type = parts[0]
                weapon_name = parts[1]
                reload_time = parts[2]
                scope_info = parts[3]
                switch_time = parts[4]
                pros_cons = parts[5]

                # 解析利弊信息
                pros_pattern = r'利：(.*?)(?=；弊：|$)'
                cons_pattern = r'弊：(.*?)(?=；利：|$)'

                pros_match = re.search(pros_pattern, pros_cons)
                cons_match = re.search(cons_pattern, pros_cons)

                pros = pros_match.group(1) if pros_match else ""
                cons = cons_match.group(1) if cons_match else ""

                weapons_list.append({
                    'weapon_type': weapon_type,
                    'weapon_name': weapon_name,
                    'reload_time': reload_time,
                    'scope_info': scope_info,
                    'switch_time': switch_time,
                    'pros': pros,
                    'cons': cons,
                    'pros_cons': pros_cons,
                    'weapon_icon': weapon_type_icons.get(weapon_type, "⚔️")
                })

        return pd.DataFrame(weapons_list)

    # 英雄相关查询方法
    def get_heroes_by_position(self, position: str) -> pd.DataFrame:
        """根据定位获取英雄列表"""
        return self.heroes_data[self.heroes_data['position'] == position]

    def get_heroes_by_difficulty(self, difficulty: str) -> pd.DataFrame:
        """根据操作难度获取英雄列表"""
        return self.heroes_data[self.heroes_data['difficulty'] == difficulty]

    def search_hero(self, hero_name: str) -> Optional[pd.Series]:
        """搜索特定英雄"""
        results = self.heroes_data[self.heroes_data['hero_name'] == hero_name]
        return results.iloc[0] if not results.empty else None

    def find_heroes_by_skill(self, skill_keyword: str) -> pd.DataFrame:
        """根据技能关键词查找英雄"""
        return self.heroes_data[self.heroes_data['skills'].str.contains(skill_keyword, na=False)]

    # 武器相关查询方法
    def get_weapons_by_type(self, weapon_type: str) -> pd.DataFrame:
        """根据武器类型获取武器列表"""
        return self.weapons_data[self.weapons_data['weapon_type'] == weapon_type]

    def search_weapon(self, weapon_name: str) -> Optional[pd.Series]:
        """搜索特定武器"""
        results = self.weapons_data[self.weapons_data['weapon_name'] == weapon_name]
        return results.iloc[0] if not results.empty else None

    def find_weapons_by_performance(self, is_advantage: bool, keyword: str) -> pd.DataFrame:
        """根据性能关键词查找武器"""
        if is_advantage:
            return self.weapons_data[self.weapons_data['pros'].str.contains(keyword, na=False)]
        else:
            return self.weapons_data[self.weapons_data['cons'].str.contains(keyword, na=False)]

    # 辅助方法
    def find_footstep_similarities(self) -> Dict[str, List[str]]:
        """查找脚步声相似的英雄组"""
        similarity_groups = {}

        for _, hero in self.heroes_data.iterrows():
            footsteps = hero['footsteps']

            # 检查是否有"相近"、"归为一组"、"与"等标识相似性的关键词
            similar_heroes = []
            if '相近' in footsteps or '归为一组' in footsteps or '与' in footsteps:
                # 提取可能提到的其他英雄名称
                for _, other_hero in self.heroes_data.iterrows():
                    if other_hero['hero_name'] != hero['hero_name'] and other_hero['hero_name'] in footsteps:
                        similar_heroes.append(other_hero['hero_name'])

            if similar_heroes:
                group_key = f"{hero['hero_name']} 组"
                similarity_groups[group_key] = [hero['hero_name']] + similar_heroes

        return similarity_groups

def apply_custom_css():
    """应用自定义CSS样式"""
    st.markdown(f"""
    <style>
        /* 全局样式 */
        body {{
            background-color: {COLORS['background']};
            color: {COLORS['text']};
        }}
        
        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS['header']};
            font-weight: bold;
        }}
        
        /* 侧边栏样式 */
        .sidebar .sidebar-content {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text']};
        }}
        
        /* 按钮样式 */
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: white;
            border-radius: 5px;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
        }}
        
        /* 优化按钮悬停效果，减少亮度降低量 */
        .stButton > button:hover {{
            background-color: #{max(0, int(COLORS['primary'][1:], 16) - 0x080808):06x};
        }}
        
        /* 选择框样式 */
        .stSelectbox > div > div {{
            background-color: {COLORS['card_bg']};
            color: {COLORS['text']};
        }}
        
        /* 卡片样式 */
        .card {{
            background-color: {COLORS['card_bg']};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* 数据框样式 */
        .dataframe-container {{
            background-color: {COLORS['card_bg']};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        
        /* 指标卡片 */
        .metric-card {{
            background-color: {COLORS['card_bg']};
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }}
        
        /* 英雄卡片 */
        .hero-card {{
            background-color: {COLORS['card_bg']};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .hero-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }}
        
        /* 武器卡片 */
        .weapon-card {{
            background-color: {COLORS['card_bg']};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .weapon-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }}
    </style>
    """, unsafe_allow_html=True)

def app():
    """Streamlit应用主函数"""
    # 应用自定义CSS
    apply_custom_css()

    # 设置页面标题和Logo
    st.markdown(f"<h1 style='text-align: center; color: {COLORS['primary']};'>⚔️ 无畏契约信息管理系统 ⚔️</h1>", unsafe_allow_html=True)

    # 初始化系统
    system = ValorantInfoSystem()

    # 创建侧边栏导航
    st.sidebar.markdown(f"<h2 style='color: {COLORS['primary']};'>导航菜单</h2>", unsafe_allow_html=True)
    menu_option = st.sidebar.selectbox(
        "选择功能",
        ["首页概览", "英雄信息", "武器信息", "英雄脚步声分析", "英雄-武器匹配分析"]
    )

    # 首页概览
    if menu_option == "首页概览":
        st.markdown(f"<h2 style='color: {COLORS['primary']};'>📊 首页概览</h2>", unsafe_allow_html=True)

        # 创建统计卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {COLORS['success']};'>{len(system.heroes_data)}</h3>
                <p style='color: {COLORS['text_secondary']};'>英雄总数</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {COLORS['warning']};'>{len(system.weapons_data)}</h3>
                <p style='color: {COLORS['text_secondary']};'>武器总数</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {COLORS['accent']};'>{len(set(system.heroes_data['position']))}</h3>
                <p style='color: {COLORS['text_secondary']};'>英雄定位</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {COLORS['danger']};'>{len(set(system.weapons_data['weapon_type']))}</h3>
                <p style='color: {COLORS['text_secondary']};'>武器类型</p>
            </div>
            """, unsafe_allow_html=True)

        # 英雄分布统计
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>🎭 英雄分布统计</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 按定位统计
            position_counts = system.heroes_data['position'].value_counts()
            fig, ax = plt.figure(figsize=(8, 6)), plt.gca()
            ax.bar(position_counts.index, position_counts.values, color=[POSITION_COLORS[pos] for pos in position_counts.index])
            plt.title("英雄按定位分布", color=COLORS['text'])
            plt.xlabel("定位", color=COLORS['text_secondary'])
            plt.ylabel("数量", color=COLORS['text_secondary'])
            plt.xticks(color=COLORS['text_secondary'])
            plt.yticks(color=COLORS['text_secondary'])
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            # 按难度统计
            difficulty_counts = system.heroes_data['difficulty'].value_counts()
            fig, ax = plt.figure(figsize=(8, 6)), plt.gca()
            ax.bar(difficulty_counts.index, difficulty_counts.values, color=[DIFFICULTY_COLORS[diff] for diff in difficulty_counts.index])
            plt.title("英雄按难度分布", color=COLORS['text'])
            plt.xlabel("难度", color=COLORS['text_secondary'])
            plt.ylabel("数量", color=COLORS['text_secondary'])
            plt.xticks(color=COLORS['text_secondary'])
            plt.yticks(color=COLORS['text_secondary'])
            plt.tight_layout()
            st.pyplot(fig)

        # 武器类型分布
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>🔫 武器类型分布</h3>", unsafe_allow_html=True)
        weapon_type_counts = system.weapons_data['weapon_type'].value_counts()
        fig, ax = plt.figure(figsize=(10, 6)), plt.gca()
        ax.bar(weapon_type_counts.index, weapon_type_counts.values, color=COLORS['primary'])
        plt.title("武器按类型分布", color=COLORS['text'])
        plt.xlabel("武器类型", color=COLORS['text_secondary'])
        plt.ylabel("数量", color=COLORS['text_secondary'])
        plt.xticks(color=COLORS['text_secondary'])
        plt.yticks(color=COLORS['text_secondary'])
        plt.tight_layout()
        st.pyplot(fig)

    # 英雄信息页面
    elif menu_option == "英雄信息":
        st.markdown(f"<h2 style='color: {COLORS['primary']};'>🎭 英雄信息</h2>", unsafe_allow_html=True)

        # 英雄查询选项卡
        tab1, tab2, tab3, tab4 = st.tabs(["按定位筛选", "按难度筛选", "搜索特定英雄", "按技能关键词查找"])

        with tab1:
            position = st.selectbox("选择英雄定位", list(set(system.heroes_data['position'])))
            if st.button("查询"):
                heroes_df = system.get_heroes_by_position(position)
                if not heroes_df.empty:
                    cols = st.columns(3)
                    for i, (_, hero) in enumerate(heroes_df.iterrows()):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class='hero-card'>
                                <h4 style='color: {hero['position_color']};'>{hero['position_icon']} {hero['hero_name']}</h4>
                                <p style='margin: 0; color: {hero['difficulty_color']};'>{hero['difficulty_icon']} 难度: {hero['difficulty']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skills']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>脚步声:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['footsteps']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能时间:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skill_time']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("未找到符合条件的英雄")

        with tab2:
            difficulty = st.selectbox("选择操作难度", list(set(system.heroes_data['difficulty'])))
            if st.button("查询", key="difficulty_query"):
                heroes_df = system.get_heroes_by_difficulty(difficulty)
                if not heroes_df.empty:
                    cols = st.columns(3)
                    for i, (_, hero) in enumerate(heroes_df.iterrows()):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class='hero-card'>
                                <h4 style='color: {hero['position_color']};'>{hero['position_icon']} {hero['hero_name']}</h4>
                                <p style='margin: 0; color: {hero['difficulty_color']};'>{hero['difficulty_icon']} 难度: {hero['difficulty']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skills']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>脚步声:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['footsteps']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能时间:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skill_time']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("未找到符合条件的英雄")

        with tab3:
            hero_name = st.text_input("输入英雄名称")
            if st.button("查询", key="hero_search"):
                hero = system.search_hero(hero_name)
                if hero is not None:
                    st.markdown(f"""
                    <div class='hero-card'>
                        <h4 style='color: {hero['position_color']};'>{hero['position_icon']} {hero['hero_name']}</h4>
                        <p style='margin: 0; color: {hero['difficulty_color']};'>{hero['difficulty_icon']} 难度: {hero['difficulty']}</p>
                        <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能:</strong></p>
                        <p style='margin: 0; color: {COLORS['text']};'>{hero['skills']}</p>
                        <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>脚步声:</strong></p>
                        <p style='margin: 0; color: {COLORS['text']};'>{hero['footsteps']}</p>
                        <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能时间:</strong></p>
                        <p style='margin: 0; color: {COLORS['text']};'>{hero['skill_time']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"未找到名为 '{hero_name}' 的英雄")

        with tab4:
            skill_keyword = st.text_input("输入技能关键词")
            if st.button("查询", key="skill_query"):
                heroes_df = system.find_heroes_by_skill(skill_keyword)
                if not heroes_df.empty:
                    cols = st.columns(3)
                    for i, (_, hero) in enumerate(heroes_df.iterrows()):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class='hero-card'>
                                <h4 style='color: {hero['position_color']};'>{hero['position_icon']} {hero['hero_name']}</h4>
                                <p style='margin: 0; color: {hero['difficulty_color']};'>{hero['difficulty_icon']} 难度: {hero['difficulty']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skills']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>脚步声:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['footsteps']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>技能时间:</strong></p>
                                <p style='margin: 0; color: {COLORS['text']};'>{hero['skill_time']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning(f"未找到包含技能关键词 '{skill_keyword}' 的英雄")

    # 武器信息页面
    elif menu_option == "武器信息":
        st.markdown(f"<h2 style='color: {COLORS['primary']};'>🔫 武器信息</h2>", unsafe_allow_html=True)

        # 武器查询选项卡
        tab1, tab2, tab3 = st.tabs(["按类型筛选", "搜索特定武器", "按性能关键词查找"])

        with tab1:
            weapon_type = st.selectbox("选择武器类型", list(set(system.weapons_data['weapon_type'])))
            if st.button("查询", key="weapon_type_query"):
                weapons_df = system.get_weapons_by_type(weapon_type)
                if not weapons_df.empty:
                    cols = st.columns(2)
                    for i, (_, weapon) in enumerate(weapons_df.iterrows()):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class='weapon-card'>
                                <h4 style='color: {COLORS['primary']};'>{weapon['weapon_icon']} {weapon['weapon_name']}</h4>
                                <p style='margin: 0; color: {COLORS['text_secondary']};'>类型: {weapon['weapon_type']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>换弹时间:</strong> {weapon['reload_time']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>开镜信息:</strong> {weapon['scope_info']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>切换时间:</strong> {weapon['switch_time']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>优点:</strong> {weapon['pros']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>缺点:</strong> {weapon['cons']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("未找到符合条件的武器")

        with tab2:
            weapon_name = st.text_input("输入武器名称")
            if st.button("查询", key="weapon_search"):
                weapon = system.search_weapon(weapon_name)
                if weapon is not None:
                    st.markdown(f"""
                    <div class='weapon-card'>
                        <h4 style='color: {COLORS['primary']};'>{weapon['weapon_icon']} {weapon['weapon_name']}</h4>
                        <p style='margin: 0; color: {COLORS['text_secondary']};'>类型: {weapon['weapon_type']}</p>
                        <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>换弹时间:</strong> {weapon['reload_time']}</p>
                        <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>开镜信息:</strong> {weapon['scope_info']}</p>
                        <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>切换时间:</strong> {weapon['switch_time']}</p>
                        <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>优点:</strong> {weapon['pros']}</p>
                        <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>缺点:</strong> {weapon['cons']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"未找到名为 '{weapon_name}' 的武器")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                keyword_type = st.radio("查询类型", ["优点", "缺点"])
            with col2:
                performance_keyword = st.text_input("输入性能关键词")

            if st.button("查询", key="performance_query"):
                is_advantage = keyword_type == "优点"
                weapons_df = system.find_weapons_by_performance(is_advantage, performance_keyword)
                if not weapons_df.empty:
                    cols = st.columns(2)
                    for i, (_, weapon) in enumerate(weapons_df.iterrows()):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class='weapon-card'>
                                <h4 style='color: {COLORS['primary']};'>{weapon['weapon_icon']} {weapon['weapon_name']}</h4>
                                <p style='margin: 0; color: {COLORS['text_secondary']};'>类型: {weapon['weapon_type']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>换弹时间:</strong> {weapon['reload_time']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>开镜信息:</strong> {weapon['scope_info']}</p>
                                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>切换时间:</strong> {weapon['switch_time']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>优点:</strong> {weapon['pros']}</p>
                                <p style='margin: 0.5rem 0; color: {COLORS['text']};'><strong>缺点:</strong> {weapon['cons']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning(f"未找到{'具有' if is_advantage else '存在'}{keyword_type}包含关键词 '{performance_keyword}' 的武器")

    # 英雄脚步声分析页面
    elif menu_option == "英雄脚步声分析":
        st.markdown(f"<h2 style='color: {COLORS['primary']};'>👣 英雄脚步声分析</h2>", unsafe_allow_html=True)

        # 显示所有英雄的脚步声信息
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>所有英雄脚步声详情</h3>", unsafe_allow_html=True)

        # 按定位分组显示
        for position in set(system.heroes_data['position']):
            st.markdown(f"<h4 style='color: {POSITION_COLORS.get(position, COLORS['primary'])};'>{POSITION_ICONS.get(position, '🎮')} {position}</h4>", unsafe_allow_html=True)

            position_heroes = system.heroes_data[system.heroes_data['position'] == position]
            for _, hero in position_heroes.iterrows():
                st.markdown(f"""
                <div class='card'>
                    <p style='margin: 0; color: {COLORS['text']};'><strong>{hero['hero_name']}:</strong> {hero['footsteps']}</p>
                </div>
                """, unsafe_allow_html=True)

    # 英雄-武器匹配分析页面
    elif menu_option == "英雄-武器匹配分析":
        st.markdown(f"<h2 style='color: {COLORS['primary']};'>🎯 英雄-武器匹配分析</h2>", unsafe_allow_html=True)

        # 基于英雄特性推荐武器
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>基于英雄特性的武器推荐</h3>", unsafe_allow_html=True)

        # 推荐逻辑示例
        recommendations = {
            "先锋": {
                "推荐武器类型": ["步枪", "霰弹枪"],
                "推荐理由": "先锋英雄通常需要快速突进和清场，步枪提供中距离火力，霰弹枪适合近距离战斗"
            },
            "决斗": {
                "推荐武器类型": ["狙击枪", "步枪"],
                "推荐理由": "决斗英雄专注于击杀，狙击枪提供高爆发，步枪提供灵活的中距离战斗能力"
            },
            "控场": {
                "推荐武器类型": ["步枪", "冲锋枪"],
                "推荐理由": "控场英雄需要持续输出和灵活移动，步枪提供稳定火力，冲锋枪适合近距离战斗"
            },
            "哨位": {
                "推荐武器类型": ["狙击枪", "步枪"],
                "推荐理由": "哨位英雄需要远距离防守，狙击枪提供远程压制，步枪提供稳定的中距离防守能力"
            }
        }

        # 显示推荐
        for position, rec in recommendations.items():
            st.markdown(f"<h4 style='color: {POSITION_COLORS.get(position, COLORS['primary'])};'>{POSITION_ICONS.get(position, '🎮')} {position}</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='card'>
                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>推荐武器类型:</strong> {', '.join(rec['推荐武器类型'])}</p>
                <p style='margin: 0.3rem 0; color: {COLORS['text']};'><strong>推荐理由:</strong> {rec['推荐理由']}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()