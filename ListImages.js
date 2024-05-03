const fs = require('fs');
const path = require('path');

const imagesDirectory = './img';
const basePath = './img/';

fs.readdir(imagesDirectory, (err, files) => {
  if (err) {
    console.error("Could not list the directory.", err);
    process.exit(1);
  }

  const imagePaths = files
    .filter(file => /\.(jpg|jpeg|png|gif)$/i.test(file)) // 过滤出图片文件
    .map(file => basePath + file); // 生成完整路径

  console.log(imagePaths); // 打印或者以其他方式使用图片路径数组
});
