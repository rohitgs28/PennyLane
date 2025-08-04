
export function getTotalPages(total: number, pageSize: number): number {
    return Math.max(1, Math.ceil(total / pageSize));
}

export function buildPageNumbers(
    totalPages: number,
    currentPage: number,
    maxButtons = 7
): (number | '…')[] {
    const nums: (number | '…')[] = [];
    if (totalPages <= maxButtons) {
        for (let i = 1; i <= totalPages; i++) nums.push(i);
        return nums;
    }
    const add = (n: number | '…') => nums.push(n);
    add(1);
    if (currentPage > 4) add('…');
    const start = Math.max(2, currentPage - 2);
    const end = Math.min(totalPages - 1, currentPage + 2);
    for (let i = start; i <= end; i++) add(i);
    if (currentPage < totalPages - 3) add('…');
    add(totalPages);
    return nums;
}
