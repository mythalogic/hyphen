FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build SvelteKit (for production)
RUN npm run build

# Expose port
EXPOSE 5173

# Run dev server (development mode)
CMD ["npm", "run", "dev", "--", "--host"]
