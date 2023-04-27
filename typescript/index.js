// Program to implement bubble sort using recursion
function bubbleSort(arr, n) {
    if (n == 1)
        return;
    for (var i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            var temp = arr[i];
            arr[i] = arr[i + 1];
            arr[i + 1] = temp;
        }
    }
    bubbleSort(arr, n - 1);
}
function printArray(arr, size) {
    for (var i = 0; i < size; i++) {
        console.log(arr[i]);
    }
}
var arr = [64, 34, 25, 12, 22, 11, 90];
var n = arr.length;
bubbleSort(arr, n);
console.log("Sorted array : ");
printArray(arr, n);
