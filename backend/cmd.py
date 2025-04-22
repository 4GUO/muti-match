from datetime import datetime

from cfi import cfi22


class PyCharmUI:
    def __init__(self):
        self.classifier = cfi22()
        self._print_welcome()

    def _print_welcome(self):
        """彩色欢迎界面"""
        print("\033[1;36m")
        print("=" * 60)
        print("医疗器械智能分类系统".center(50))
        print(f"数据版本: {datetime.now().strftime('%Y-%m-%d')}".center(50))
        print("=" * 60)
        print("\033[0m")
        print("提示：")
        print("- 输入设备名称进行搜索（如'血糖仪'）")
        print("- 输入 'q' 退出程序")
        print("- 支持模糊匹配和语义搜索两种模式\n")

    def run(self):
        while True:
            try:
                query = input("\n🔍 请输入医疗器械名称：").strip()

                if query.lower() in ('q', 'quit', 'exit'):
                    print("\n👋 感谢使用，再见！")
                    break

                if len(query) < self.classifier.config.MIN_QUERY_LEN:
                    print(f"⚠️ 查询太短，请至少输入{self.classifier.config.MIN_QUERY_LEN}个字符")
                    continue

                # 选择搜索模式
                print("\n请选择搜索模式：")
                print("1. 快速模糊匹配（适合精确名称）")
                print("2. 智能语义搜索（推荐，适合模糊查询）")
                choice = input("请输入选择（默认2）：").strip() or "2"

                # 执行搜索
                start_time = datetime.now()
                if choice == "1":
                    results = self.classifier.fuzzy_search(query, self.classifier.config.MAX_RESULTS)
                    search_type = "模糊匹配"
                else:
                    results = self.classifier.semantic_search(query, self.classifier.config.MAX_RESULTS)
                    search_type = "语义搜索"

                # 显示结果
                self._display_results(results, search_type, datetime.now() - start_time)

            except KeyboardInterrupt:
                print("\n🛑 操作已中断")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                # 输出详细错误信息，帮助调试
                import traceback
                traceback.print_exc()

    def _display_results(self, results, search_type, elapsed):
        """美化结果显示"""
        if not results:
            print("\n⚠️ 未找到匹配结果，请尝试其他关键词")
            return

        print(f"\n✨ {search_type}结果（耗时 {elapsed.total_seconds():.2f} 秒）")
        print("-" * 90)
        print(f"{'排名':<5}{'名称':<30}{'分类编码':<15}{'层级':<10}{'匹配度':<10}{'用途描述'}")
        print("-" * 90)

        for i, item in enumerate(results, 1):
            name = str(item.get('name', '未知名称'))[:28]  # 确保name是字符串并截取
            code = str(item.get('code', '未知编码'))  # 确保code是字符串
            level = item.get('level', '未知层级')  # 如果没有层级数据，提供默认值
            score = float(item.get('score', 0))  # 确保score是浮动数字
            # exp 通过 exp 和 description 两个字段合并
            exp = "【品名】:" + item.get('exp', '') + " 【用途】" + item.get('description', '')

            print(
                str(i) + " " + str(name).ljust(30) +
                str(code).ljust(15) +
                str(level).ljust(10) +
                "{:.2f}".format(score).ljust(10) +
                str(exp)[:100] + "..."
            )
