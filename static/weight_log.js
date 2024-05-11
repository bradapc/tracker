//Creates a visualizer of the BMI scale
//BMI scale goes from <18 (underweight) to >45 (severely obese)
//For representation, BMI scale will go as low as 0 and as high as 60
//For representation, multiply each entry by 20.

bmi_visualizer = document.querySelector(".bmi-visualizer");

class BMICategory {
    constructor(min, max, name, color) {
        this.min = min;
        this.max = max;
        this.name = name;
        this.color = color;
    }
};

const underweight = new BMICategory(0, 18, "Underweight", "#84acd1");
const normal_weight = new BMICategory(18, 25, "Normal", "#3bcc62");
const overweight = new BMICategory(25, 30, "Overweight", "#e7da31");
const obese = new BMICategory(30, 45, "Obese", "#f57c2d");
const severely_obese = new BMICategory(45, 60, "Severely Obese", "#f15052");
const categories = [underweight, normal_weight, overweight, obese, severely_obese];

function renderBMIScale(current_bmi){
    for (i = 0; i < categories.length; i++) {
        const bmiVisualizerWrapper = document.createElement("div");
        const bmiTextWrapper = document.createElement("div");
        const bmiColorWrapper = document.createElement("div");
        width_diff = categories[i].max - categories[i].min;
        const bmiTextDiv = document.createElement("div");
        bmiTextDiv.innerHTML = categories[i].min + "-" + categories[i].max;
        bmiTextDiv.width = width_diff * 20 + "px";
        bmiTextDiv.style.textAlign = "center";
        const bmiColorDiv = document.createElement("div");
        bmiColorDiv.style.width = width_diff * 20 + "px";
        bmiColorDiv.style.height = 100 + "px";
        bmiColorDiv.style.backgroundColor = categories[i].color;
        bmiColorDiv.innerHTML = categories[i].name;
        bmiColorDiv.style.textAlign = "center";

        bmiTextWrapper.appendChild(bmiTextDiv);
        bmiColorWrapper.appendChild(bmiColorDiv);

        if (current_bmi >= categories[i].min && current_bmi <= categories[i].max)
            {
                bmi_padding_left = ((current_bmi - categories[i].min) / (categories[i].max - categories[i].min) * width_diff * 20);
                console.log(bmi_padding_left);
                const bmiDivLine = document.createElement("div");
                bmiDivLine.style.height = 100 + "px";
                bmiDivLine.style.top = "-24px";
                bmiDivLine.style.width = 2 + "px";
                bmiDivLine.style.backgroundColor = "red";
                bmiDivLine.style.zIndex = "1";
                bmiDivLine.style.position = "relative";
                bmiDivLine.style.left = bmi_padding_left + "px";
                bmiColorDiv.appendChild(bmiDivLine);
            }

        bmiVisualizerWrapper.appendChild(bmiTextWrapper);
        bmiVisualizerWrapper.appendChild(bmiColorWrapper);
        bmi_visualizer.appendChild(bmiVisualizerWrapper);
    }
};