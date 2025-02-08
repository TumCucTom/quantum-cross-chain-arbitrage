# Use Node.js image
FROM node:16

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy application files
COPY . .

# Start React app
CMD ["yarn", "start"]
