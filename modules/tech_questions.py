from utils.llm_utils import get_llm_response
from config.config import Config

class TechQuestionGenerator:
    """Generates technical questions based on the candidate's tech stack."""
    
    def __init__(self):
        """Initialize the tech question generator."""
        # Dictionary of common technologies and sample questions
        # This serves as a fallback if the LLM is not available
        self.question_templates = {
            "python": [
                "What are Python decorators and how do you use them?",
                "Explain the difference between lists and tuples in Python.",
                "How does memory management work in Python?",
                "What is the Global Interpreter Lock (GIL) and how does it affect multithreaded Python programs?",
                "Explain the concept of list comprehensions and provide an example."
            ],
            "javascript": [
                "Explain the concept of closures in JavaScript.",
                "What is the difference between '==' and '===' operators?",
                "How does prototypal inheritance work in JavaScript?",
                "Explain the event loop in JavaScript.",
                "What are Promises and how do they differ from callbacks?"
            ],
            "java": [
                "What is the difference between an interface and an abstract class in Java?",
                "Explain the concept of Java's Garbage Collection.",
                "What are the key features introduced in Java 8?",
                "How does multithreading work in Java?",
                "Explain the principles of SOLID in Java programming."
            ],
            "react": [
                "What is the virtual DOM and how does React use it?",
                "Explain the component lifecycle in React.",
                "What are hooks in React and how do you use them?",
                "How do you manage state in a React application?",
                "Explain the concept of props and state in React components."
            ],
            "angular": [
                "What is dependency injection in Angular?",
                "Explain the difference between components and directives in Angular.",
                "How does change detection work in Angular?",
                "What are Angular modules and how do they help organize code?",
                "Explain the concept of services in Angular."
            ],
            "vue": [
                "What is the Vue instance lifecycle?",
                "Explain the difference between computed properties and methods in Vue.",
                "How does Vue's reactivity system work?",
                "What are Vue directives and how do you create custom directives?",
                "Explain the concept of mixins in Vue."
            ],
            "node.js": [
                "How does the event loop work in Node.js?",
                "What is the purpose of middleware in Express.js?",
                "Explain the difference between process.nextTick() and setImmediate().",
                "How do you handle asynchronous operations in Node.js?",
                "What are streams in Node.js and how are they used?"
            ],
            "django": [
                "Explain Django's MTV (Model-Template-View) architecture.",
                "How do you create a custom middleware in Django?",
                "What are Django signals and how are they used?",
                "Explain Django's ORM and how it interacts with databases.",
                "How do you handle authentication and authorization in Django?"
            ],
            "flask": [
                "What is the application factory pattern in Flask?",
                "How do you handle database operations in Flask?",
                "Explain Flask's context globals (g, request, session).",
                "How do you implement authentication in a Flask application?",
                "What are Flask extensions and how do you use them?"
            ],
            "sql": [
                "Explain the difference between INNER JOIN and LEFT JOIN.",
                "What are database transactions and how do they ensure data integrity?",
                "How do you optimize a slow SQL query?",
                "Explain normalization and denormalization in database design.",
                "What are indexes and how do they improve query performance?"
            ],
            "mongodb": [
                "What is sharding in MongoDB and how does it work?",
                "Explain the concept of document embedding vs. referencing in MongoDB.",
                "How do you ensure data consistency in a MongoDB database?",
                "What are MongoDB aggregation pipelines?",
                "Explain the concept of indexing in MongoDB."
            ],
            "docker": [
                "What is the difference between a Docker image and a container?",
                "How do you persist data in Docker containers?",
                "Explain Docker networking and how containers communicate.",
                "What is Docker Compose and how is it used?",
                "How do you optimize Docker images for production?"
            ],
            "kubernetes": [
                "What are Kubernetes pods and how do they work?",
                "Explain the difference between a Deployment and a StatefulSet in Kubernetes.",
                "How does service discovery work in Kubernetes?",
                "What are Kubernetes operators and when would you use them?",
                "Explain Kubernetes resource limits and requests."
            ],
            "aws": [
                "What is the difference between EC2 and Lambda?",
                "How do you design a highly available architecture in AWS?",
                "Explain AWS IAM and best practices for security.",
                "What are the different storage options in AWS and when would you use each?",
                "How do you implement auto-scaling in AWS?"
            ],
            "devops": [
                "Explain the concept of Infrastructure as Code.",
                "What is CI/CD and how does it improve the development process?",
                "How do you monitor applications in production?",
                "What strategies do you use for database migrations in a CI/CD pipeline?",
                "Explain the concept of blue-green deployment."
            ],
            "machine learning": [
                "What is the difference between supervised and unsupervised learning?",
                "Explain overfitting and how to prevent it.",
                "What evaluation metrics do you use for classification problems?",
                "How do you handle imbalanced datasets?",
                "Explain the concept of feature engineering and why it's important."
            ],
            "data science": [
                "What is the difference between correlation and causation?",
                "How do you handle missing data in a dataset?",
                "Explain the concept of dimensionality reduction and when you would use it.",
                "What statistical tests do you use to validate hypotheses?",
                "How do you communicate data insights to non-technical stakeholders?"
            ]
        }
    
    def normalize_tech_name(self, tech):
        """Normalize technology names for matching with templates.
        
        Args:
            tech (str): The technology name to normalize
            
        Returns:
            str: The normalized technology name
        """
        tech_lower = tech.lower()
        
        # Map common variations to standard names
        tech_mapping = {
            "js": "javascript",
            "py": "python",
            "react.js": "react",
            "reactjs": "react",
            "vue.js": "vue",
            "vuejs": "vue",
            "angular.js": "angular",
            "angularjs": "angular",
            "node": "node.js",
            "nodejs": "node.js",
            "postgres": "postgresql",
            "postgres sql": "postgresql",
            "mongo": "mongodb",
            "k8s": "kubernetes",
            "ml": "machine learning",
            "ai": "machine learning",
            "artificial intelligence": "machine learning"
        }
        
        return tech_mapping.get(tech_lower, tech_lower)
    
    def get_questions_from_template(self, tech, num_questions=3):
        """Get questions for a technology from the templates.
        
        Args:
            tech (str): The technology to get questions for
            num_questions (int): The number of questions to return
            
        Returns:
            list: A list of questions for the technology
        """
        normalized_tech = self.normalize_tech_name(tech)
        
        if normalized_tech in self.question_templates:
            questions = self.question_templates[normalized_tech]
            return questions[:min(num_questions, len(questions))]
        else:
            # If we don't have templates for this technology, return generic questions
            return [
                f"What experience do you have with {tech}?",
                f"Describe a challenging problem you solved using {tech}.",
                f"What are the best practices you follow when working with {tech}?"
            ]
    
    def determine_question_count(self, experience_years):
        """Determine the number of questions based on experience level.
        
        Args:
            experience_years (str): Years of experience as a string
            
        Returns:
            int: Number of questions (3-4)
        """
        try:
            # Extract numeric value from experience string
            import re
            years_match = re.search(r'(\d+)', str(experience_years))
            if years_match:
                years = int(years_match.group(1))
                if years <= 2:
                    return 3  # Junior level - 3 questions
                else:
                    return 4  # Mid/Senior level - 4 questions
            else:
                return 3  # Default to 3 questions
        except:
            return 3  # Default to 3 questions
    
    def generate_combined_questions_with_llm(self, tech_stack, experience_years):
        """Generate combined questions across all tech stacks using the LLM.
        
        Args:
            tech_stack (list): List of technologies
            experience_years (str): Years of experience
            
        Returns:
            list: A list of combined questions
        """
        question_count = self.determine_question_count(experience_years)
        
        # Create a prompt for the LLM
        prompt = f"""
        You are a technical interviewer for a tech recruitment agency. Generate {question_count} technical interview questions 
        that cover the following technologies: {', '.join(tech_stack)}.
        
        The questions should:
        1. Be challenging but appropriate for a candidate with {experience_years} years of experience
        2. Test both theoretical knowledge and practical application
        3. Reveal the depth of the candidate's understanding
        4. Cover multiple technologies in a single question when possible
        5. Be clear and concise
        6. Focus on real-world scenarios and problem-solving
        
        Format your response as a JSON array of questions.
        Example format:
        ["Question 1", "Question 2", "Question 3"]
        
        Make sure the questions are comprehensive and test the candidate's ability to work with the combined tech stack.
        """
        
        try:
            # Try to get a response from the LLM
            response = get_llm_response(prompt, response_format="json")
            
            # Parse the response as a list
            if isinstance(response, list):
                # Ensure we have the right number of questions
                if len(response) >= question_count:
                    return response[:question_count]
                else:
                    # If LLM returned fewer questions, pad with template questions
                    return self._pad_questions_with_templates(response, tech_stack, question_count)
            else:
                # Fallback to templates if response is not a list
                return self.generate_combined_questions_from_templates(tech_stack, experience_years)
        except Exception as e:
            # If there's an error with the LLM, fall back to templates
            print(f"Error generating questions with LLM: {e}")
            return self.generate_combined_questions_from_templates(tech_stack, experience_years)
    
    def _pad_questions_with_templates(self, llm_questions, tech_stack, target_count):
        """Pad LLM questions with template questions to reach target count.
        
        Args:
            llm_questions (list): Questions from LLM
            tech_stack (list): List of technologies
            target_count (int): Target number of questions
            
        Returns:
            list: Padded list of questions
        """
        padded_questions = llm_questions.copy()
        
        # Get template questions for each tech
        all_template_questions = []
        for tech in tech_stack:
            tech_questions = self.get_questions_from_template(tech, 2)
            all_template_questions.extend(tech_questions)
        
        # Add template questions until we reach target count
        for question in all_template_questions:
            if len(padded_questions) >= target_count:
                break
            if question not in padded_questions:
                padded_questions.append(question)
        
        return padded_questions[:target_count]
    
    def generate_combined_questions_from_templates(self, tech_stack, experience_years):
        """Generate combined questions from templates across all tech stacks.
        
        Args:
            tech_stack (list): List of technologies
            experience_years (str): Years of experience
            
        Returns:
            list: A list of combined questions
        """
        question_count = self.determine_question_count(experience_years)
        all_questions = []
        
        # Collect questions from all tech stacks
        for tech in tech_stack:
            tech_questions = self.get_questions_from_template(tech, 2)
            all_questions.extend(tech_questions)
        
        # Shuffle and select the required number of questions
        import random
        random.shuffle(all_questions)
        
        # Ensure we have enough questions
        if len(all_questions) < question_count:
            # Add some generic cross-tech questions
            generic_questions = [
                "How do you approach learning new technologies?",
                "Describe a project where you integrated multiple technologies.",
                "How do you handle debugging across different technology stacks?",
                "What's your approach to code review and quality assurance?",
                "How do you stay updated with the latest technology trends?"
            ]
            all_questions.extend(generic_questions)
        
        return all_questions[:question_count]
    
    def generate_combined_questions(self, tech_stack, experience_years):
        """Generate combined technical questions across all tech stacks.
        
        Args:
            tech_stack (list): The candidate's tech stack
            experience_years (str): Years of experience
            
        Returns:
            list: A list of combined questions (3-4 total)
        """
        # Try to generate questions with the LLM first
        try:
            return self.generate_combined_questions_with_llm(tech_stack, experience_years)
        except Exception as e:
            # If there's an error, fall back to template-based questions
            print(f"Error generating questions with LLM: {e}")
            return self.generate_combined_questions_from_templates(tech_stack, experience_years)
    
    def get_next_question(self, questions, current_index):
        """Get the next question from the list.
        
        Args:
            questions (list): List of all questions
            current_index (int): Current question index
            
        Returns:
            tuple: (question, is_last_question, progress_info)
        """
        if current_index >= len(questions):
            return None, True, "All questions completed!"
        
        question = questions[current_index]
        is_last = current_index == len(questions) - 1
        progress = f"Question {current_index + 1} of {len(questions)}"
        
        return question, is_last, progress
    
    def format_question_with_options(self, question, current_index, total_questions):
        """Format a single question with skip option.
        
        Args:
            question (str): The question to display
            current_index (int): Current question index
            total_questions (int): Total number of questions
            
        Returns:
            str: Formatted question with options
        """
        progress = f"**Question {current_index + 1} of {total_questions}**\n\n"
        question_text = f"{question}\n\n"
        options = "**Options:**\n• Answer the question\n• Type 'skip' to move to the next question\n• Type 'done' to finish the interview"
        
        return progress + question_text + options