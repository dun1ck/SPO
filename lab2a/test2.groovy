class AccessManager {
    static void main(String[] args) {
        def role = "ADMIN"
        int level = 3
        boolean active = true
        int attempts = 0

        while (attempts < 3) {
            attempts++

            if (active) {
                if (level >= 2) {
                    if (role == "ADMIN") {
                        for (int t = 1; t <= 2; t++) {
                            if (t == 2) {
                                println "Доступ подтвержден"
                            } else {
                                println "Проверка токена: $t"
                            }
                        }
                    } else {
                        println "Недостаточно прав"
                    }
                } else {
                    println "Низкий уровень"
                }
            } else {
                println "Не активен"
            }
        }
    }
}
