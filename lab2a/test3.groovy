class CommandHandler {
    static void main(String[] args) {
        def commands = [101, 102, 103, 104, 105, 999]

        for (cmd in commands) {
            println "Команда: $cmd"

            switch (cmd) {
                case 101:
                    println "Инициализация"
                    break

                case 102:
                    println "Чтение конфигурации"
                    break

                case 103:
                    println "Запуск процесса"
                    break

                case 104:
                    String mode = (cmd % 2 == 0) ? "FAST" : "SAFE"
                    println "Синхронизация: $mode"
                    break

                case 105:
                    println "Остановка"
                    break

                default:
                    println "Неизвестная команда: $cmd"
                    break
            }
        }

        println "Готово"
    }
}
