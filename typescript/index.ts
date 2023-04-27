// Program to implement bubble sort using recursion

function bubbleSort(arr: number[], n: number): void {
    if (n == 1) return;

    for (let i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            let temp: number = arr[i];
            arr[i] = arr[i + 1];
            arr[i + 1] = temp;
        }
    }

    bubbleSort(arr, n - 1);
}

function printArray(arr: number[], size: number): void {
    for (let i = 0; i < size; i++) {
        console.log(arr[i]);
    }
}

let arr: number[] = [64, 34, 25, 12, 22, 11, 90];
let n: number = arr.length;
bubbleSort(arr, n);
console.log("Sorted array : ");
printArray(arr, n);
