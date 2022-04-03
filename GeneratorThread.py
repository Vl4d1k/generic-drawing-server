from threading import Thread
import os
from PIL import Image

from GeneticDrawing import *


class GeneratorThread(Thread):
    def __init__(self, uid, stages=100, generations=20):
        Thread.__init__(self)
        self.uid = uid
        self.stages = stages
        self.generations = generations

    def run(self):
        gen = GeneticDrawing(f'storage/uploads/{self.uid}.png', seed=time.time())
        path = f'storage/generated/{self.uid}'

        if not os.path.exists(path):
            os.mkdir(path)

        for i, image in enumerate(gen.generate(self.stages, self.generations, show_progress_imgs=False)):
            img = Image.fromarray(image)
            img.save(os.path.join(path, f"{i}.png"), quality=20)
