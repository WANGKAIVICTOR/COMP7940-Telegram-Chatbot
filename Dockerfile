# Use the image python
FROM python

# Copy the files main.py log.py and requirements.txt to the container
COPY main.py /
COPY log.py /
COPY utils.py /
COPY database.py /
COPY chatbot.py /
COPY requirements.txt /

# Install the dependency using the two pip install statements.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set the environment variables ACCESS_TOKEN , HOST , PASSWORD REDISPORT
ENV AM_I_IN_A_DOCKER_CONTAINER=True
ENV ACCESS_TOKEN=2125824444:AAGsVnRkX1W61N8XMQKH5J7bcTxLRpaqzXM
ENV HOST=z-cdb-6wk2pax5.sql.tencentcdb.com
ENV PORT=63885
ENV PASSWORD=wangkai2933
ENV USER=root
ENV DBNAME=telegram_chatbot
ENV OPENAI_KEY=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
ENV DEVELOPER_KEY=AIzaSyCaCg1kKjZAcGZ_pVNi_zfdzQ--9ln6tFk
ENV MAX_TOKEN=1000
ENV CHARACTER_DESC = I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with "Unknown".
# CHARACTeR_DESC = I want you to act as a linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. do not write explanations. do not type commands unless I instruct you to do so. when i need to tell you something in english, i will do so by putting text inside curly brackets {like this}. my first command is pwd
# Set the ENTRYPOINT and/or CMD correctly so that it will execute python main.py
ENTRYPOINT ["python", "main.py"]