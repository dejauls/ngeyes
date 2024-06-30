const calculateBricks = () => {
    const getValue = id => parseFloat(document.getElementById(id).value);
    const [length, width, height] = ['panjang', 'lebar', 'tinggi'].map(getValue);
    const warnElement = document.getElementById('warn');
    const jumlahContainer = document.getElementById('jumlah-container');

    if ([length, width, height].some(isNaN)) {
        warnElement.innerText = 'Mohon masukkan semua nilai dengan benar!';
        warnElement.style.display = 'block';
        jumlahContainer.style.display = 'none';
        return;
    } else {
        warnElement.style.display = 'none';
        jumlahContainer.style.display = 'block';
    }

    const wallArea = 2 * (length + width) * height;
    const bricksPerCubicMeterReclea = 68;
    const bricksPerCubicMeterRegular = 80;

    const brickCountReclea = Math.ceil(wallArea * bricksPerCubicMeterReclea );
    const brickCountRegular = Math.ceil(wallArea * bricksPerCubicMeterRegular );

    const formattedBrickCountReclea = new Intl.NumberFormat('id-ID').format(brickCountReclea);
    const formattedBrickCountRegular = new Intl.NumberFormat('id-ID').format(brickCountRegular);

    const brickDifference = brickCountRegular - brickCountReclea;
    const formattedBrickDifference = new Intl.NumberFormat('id-ID').format(brickDifference);

    // Display brick counts
    document.getElementById('reclea-jumlah').innerHTML = `${formattedBrickCountReclea} pcs`;
    document.getElementById('biasa-jumlah').innerHTML = `${formattedBrickCountRegular} pcs`;
    document.getElementById('diff-jumlah').innerHTML = `${formattedBrickDifference} pcs`;

    // Calculate and display cement sacks
    const cementSacksReclea = Math.ceil(brickCountReclea / 600 ); // 1 sak semen untuk 600 bata reclea
    const cementSacksRegular = Math.ceil(brickCountRegular / 300 ); // 1 sak semen untuk 300 bata biasa
    

    const formattedCementSacksReclea = new Intl.NumberFormat('id-ID').format(cementSacksReclea);
    const formattedCementSacksRegular = new Intl.NumberFormat('id-ID').format(cementSacksRegular);

    document.getElementById('semen-reclea').innerHTML = `${formattedCementSacksReclea} sak`;
    document.getElementById('semen-biasa').innerHTML = `${formattedCementSacksRegular} sak`;

    // Calculate and display cement savings
    const cementSavings = cementSacksRegular - cementSacksReclea;
    document.getElementById('semen-hemat').innerHTML = `${cementSavings} sak`;
};

['panjang', 'lebar', 'tinggi'].forEach(id => {
    document.getElementById(id).addEventListener('keyup', calculateBricks);
});
