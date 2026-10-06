class ArrayProcessor {
    static void main(String[] args) {
        def numbers = [14, 7, 22, 5, 89, 44, 3]
        int maxVal = numbers[0]
        int evenCount = 0

        for (int i = 0; i < numbers.size(); i++) {
            int current = numbers[i]

            if (current > maxVal) {
                maxVal = current
            }

            if (current % 2 == 0) {
                evenCount++
            } else {
                println "Нечетное число: $current"
            }
        }

        println "Максимум: $maxVal"
        println "Количество четных: $evenCount"
    }
}
