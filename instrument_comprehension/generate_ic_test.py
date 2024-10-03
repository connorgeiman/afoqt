import os
import random
from PIL import Image, ImageDraw, ImageFont
import re
import csv
from fpdf import FPDF

NUM_TESTS = 2

def generate_questions(save_folder):
    answers = []

    for i in range(25):
        # Open the 6 input images
        image_files = [f for f in os.listdir("instrument_comprehension/3_jets") if f.endswith(".png")]
        correct_file = random.choice(image_files)
        incorrect_files = random.sample([f for f in image_files if f != correct_file], 3)
        all_images = [correct_file] + incorrect_files
        random.shuffle(all_images)
        correct_position = all_images.index(correct_file)
        num_to_let = {0: "A", 1: "B", 2: "C", 3: "D"}
        correct_answer = num_to_let[correct_position]

        # id = re.search(r"\d+", correct_file).group()
        pattern = r"jet_(\d+)-(\d+)\.png"
        matches = re.findall(pattern, correct_file)
        id = [int(match) for match in matches[0]]
        horizon = id[0]
        compass = id[1]

        image1 = Image.open(f'instrument_comprehension/1_horizons/horizon_{horizon}.png')
        image2 = Image.open(f'instrument_comprehension/2_compasses/compass_{compass}.png')
        image3 = Image.open("instrument_comprehension/3_jets/"+all_images[0])
        image4 = Image.open("instrument_comprehension/3_jets/"+all_images[1])
        image5 = Image.open("instrument_comprehension/3_jets/"+all_images[2])
        image6 = Image.open("instrument_comprehension/3_jets/"+all_images[3])

        # Resize the second row images to be the same width
        total_width = image1.width+image2.width
        resize_width = int(total_width / 4)
        image3 = image3.resize((resize_width, int(image3.height * resize_width / image3.width)))
        image4 = image4.resize((resize_width, int(image4.height * resize_width / image4.width)))
        image5 = image5.resize((resize_width, int(image5.height * resize_width / image5.width)))
        image6 = image6.resize((resize_width, int(image6.height * resize_width / image6.width)))

        # Create a new blank image with the correct size
        scale_factor = 0.6
        firstrow_height = int(image1.height*(scale_factor+0.25))
        total_height = firstrow_height+image3.height
        new_image = Image.new("RGB", (total_width, total_height), "white")

        image1 = image1.resize((int(scale_factor*image1.width), int(scale_factor*image1.height)))
        image2 = image2.resize((int(scale_factor*image2.width), int(scale_factor*image2.height)))

        # Paste the images into the new image
        new_image.paste(image1, (int((1-scale_factor)*total_width/2), 0))
        new_image.paste(image2, (int(total_width/2), 0))
        new_image.paste(image3, (0, firstrow_height))
        new_image.paste(image4, (resize_width, firstrow_height))
        new_image.paste(image5, (resize_width * 2, firstrow_height))
        new_image.paste(image6, (resize_width * 3, firstrow_height))

        font_size = 40
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        draw = ImageDraw.Draw(new_image)
        draw.text((int(image3.width/2-14), int(firstrow_height-50)), "A", fill="black", font=font)
        draw.text((int(image3.width/2-14+image3.width), int(firstrow_height-50)), "B", fill="black", font=font)
        draw.text((int(image3.width/2-14+image3.width*2), int(firstrow_height-50)), "C", fill="black", font=font)
        draw.text((int(image3.width/2-14+image3.width*3), int(firstrow_height-50)), "D", fill="black", font=font)

        # Record the correct answer
        answers.append(f"{i+1}) {correct_answer}")

        # Save the image
        formatted_num = '{:02d}'.format(i)
        new_image.save(f"{save_folder}/question_{formatted_num}.png", format="PNG")

    return answers

def generate_test():
    folder_num = max([int(f.split("_")[1]) for f in os.listdir("instrument_comprehension/generated_tests") if f.startswith("test")] + [-1]) + 1
    save_folder = f"instrument_comprehension/generated_tests/test_{folder_num}"
    os.makedirs(save_folder, exist_ok=True)

    answer_key = generate_questions(save_folder)
    # folder = save_folder
    image_files = sorted([f for f in os.listdir(save_folder) if f.endswith('.png')])

    selected_files = image_files[:25]

    # Create a new PDF object with letter size
    pdf = FPDF(unit="pt", format="letter")

    # Set the maximum width and height of an image
    max_width = 612  # 8.5 inches * 72 dpi = 612 pt
    max_height = 648  # one-half of letter size (11 inches) in points

    num_rows = 4
    num_cols = 2

    # Iterate over the images, adding them to the grid on each page
    for i in range(0, len(selected_files), num_rows * num_cols):
        # Create a new page
        pdf.add_page()
        # Iterate over the rows of the grid
        for row in range(num_rows):
            # Iterate over the columns of the grid
            for col in range(num_cols):
                # Compute the index of the current image in the image files list
                index = i + row * num_cols + col
                # If the index is within the bounds of the image files list, add the image to the grid
                if index < len(image_files):
                    # Load the image and get its original size and aspect ratio
                    image = Image.open(f"{save_folder}/{image_files[index]}")
                    width, height = image.size
                    aspect_ratio = width / height
                    # Scale the image so that its height fits within the maximum height
                    if height > max_height:
                        width = width * max_height / height
                        height = max_height
                    # Compute the x and y coordinates of the upper-left corner of the image in the grid
                    x = col * pdf.w / num_cols
                    y = row * pdf.h / num_rows
                    # Compute the width of the image based on its original aspect ratio
                    image_width = height * aspect_ratio
                    # Check if the image width is greater than the column width
                    if image_width > pdf.w / num_cols:
                        # Scale the image width to fit within the column width
                        image_width = pdf.w / num_cols
                        # Scale the image height to maintain the original aspect ratio
                        height = image_width / aspect_ratio

                    # Add the image to the PDF at the appropriate position in the grid
                    pdf.image(f"{save_folder}/{image_files[index]}", x + (pdf.w / num_cols - image_width) / 2 + 15, y + (pdf.h / num_rows - height) / 2 + 15, w=int(0.9*image_width), h=int(0.9*height))

                    # Add sequential number to the upper left of the image
                    pdf.set_xy(x+10, y+10)
                    pdf.set_font("Arial", 'B', size=12)
                    pdf.cell(10, 20, str(index + 1))

    # add answer key to the end
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 20, txt="ANSWER KEY", ln=1, align="C")
    for line in answer_key:
        pdf.multi_cell(max_width, 20, line)

    pdf.output(f"{save_folder}/instrument_comprehension_test_{folder_num}.pdf", "F")


for i in range(NUM_TESTS): 
    generate_test()
