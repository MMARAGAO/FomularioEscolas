 const userAnswers = {{ user_answers|safe }};
  console.log(userAnswers);  // Adicione esta linha para depuração
  function markSavedResponses() {
      for (const [key, value] of Object.entries(userAnswers)) {
          const inputElement = document.querySelector(`input[name="${key}"][value="${value}"]`);
          if (inputElement) {
              inputElement.checked = true;
          }
      }
  }
  document.addEventListener('DOMContentLoaded', function () {
      markSavedResponses();

      const questions = document.querySelectorAll('.question');

      let currentQuestionIndex = 0;

      // Find the last answered question
      for (let i = 0; i < questions.length; i++) {
          const questionId = questions[i].getAttribute('data-id');
          if (userAnswers.hasOwnProperty(`response_${questionId}`)) {
              currentQuestionIndex = i;  // Update the currentQuestionIndex if an answer is found
          }
      }

      // Hide all questions initially
      questions.forEach(question => {
          question.style.display = 'none';
      });

      // Show the current question
      questions[currentQuestionIndex].style.display = 'block';

  const responseIdToText = JSON.parse(document.getElementById('response-id-to-text').textContent);

  updateButtons();
  updateProgressBar();  // Moved this line here


      function updateProgressBar() {
          const progressBar = document.querySelector('.progress-bar');
          const progress = (currentQuestionIndex / questions.length) * 100;
          progressBar.style.width = progress + '%';
          progressBar.setAttribute('aria-valuenow', progress);
      }

  function checkDependencies(question) {
      const dependsOn = question.getAttribute('data-depends-on');
      const triggerResponsesStr = question.getAttribute('data-trigger-response');

      console.log(`Checking dependencies for question: ${question.querySelector('.question-label').textContent}`);
      console.log(`dependsOn: ${dependsOn}`);
      console.log(`triggerResponsesStr: ${triggerResponsesStr}`);

      if (dependsOn) {
          const triggerResponses = triggerResponsesStr ? triggerResponsesStr.split(", ") : null;

          console.log(`triggerResponses: ${triggerResponses}`);

          const dependencyResponseElements = document.querySelectorAll(`[name=response_${dependsOn}]`);
          let dependencyResponseId;
          dependencyResponseElements.forEach((elem) => {
              if (elem.checked) {
                  dependencyResponseId = elem.value;
              }
          });

          if (dependencyResponseId) {
              const dependencyResponseText = responseIdToText[dependencyResponseId];

              console.log(`dependencyResponseText: ${dependencyResponseText}`);

              if (triggerResponses && !triggerResponses.includes(dependencyResponseText)) {
                  console.log('adasdasdasd', triggerResponses);
                  console.log('fudeu', triggerResponses.includes(dependencyResponseText));
                  console.log('Dependency not met, hiding question');
                  return false;
              }
          }
      }

      console.log('No dependencies or dependency met, showing question');
      return true;
  }


  window.saveAndContinueLater = function () {
      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

      const questions = document.querySelectorAll('.question');
      questions.forEach((question, index) => {
          const risk_factor_id = question.getAttribute('data-id');
          const checkedInput = question.querySelector('input:checked');
          if (checkedInput) {
              const response_id = checkedInput.value;
              formData.append('response_' + risk_factor_id, response_id);
          }
      });

      fetch('/save-temporary-responses/', {
          method: 'POST',
          body: formData,
      })
          .then(response => response.json())
          .then(data => {
              console.log(data);

              // Redirect to homepage after successful save
              window.location.href = '/';

          });
  };






      function checkAllDependencies() {
          questions.forEach((question, index) => {
              if (checkDependencies(question)) {
                  question.style.display = (index === currentQuestionIndex) ? 'block' : 'none';
              } else {
                  question.style.display = 'none';
              }
          });
      }

  window.nextQuestion = function () {
      const currentQuestion = questions[currentQuestionIndex];
      const hasAnswer = currentQuestion.querySelector('input:checked');
      if (!hasAnswer) {
          alert('Please answer the current question before proceeding.');
          return;
      }
      questions[currentQuestionIndex].style.display = 'none';
      do {
          currentQuestionIndex = Math.min(currentQuestionIndex + 1, questions.length - 1);
      } while (!checkDependencies(questions[currentQuestionIndex]) && currentQuestionIndex < questions.length - 1);
      questions[currentQuestionIndex].style.display = 'block';  // Adicionado esta linha
      updateProgressBar();
      updateButtons();
  };

  window.prevQuestion = function () {
      questions[currentQuestionIndex].style.display = 'none';
      do {
          currentQuestionIndex = Math.max(currentQuestionIndex - 1, 0);
      } while (!checkDependencies(questions[currentQuestionIndex]) && currentQuestionIndex > 0);
      questions[currentQuestionIndex].style.display = 'block';  // Adicionado esta linha
      updateProgressBar();
      updateButtons();
  };

  function updateButtons() {
      const nextButton = document.getElementById('next-button');
      const submitButton = document.getElementById('submit-button');
      if (currentQuestionIndex === questions.length - 1) {
          nextButton.style.display = 'none';
          submitButton.style.display = 'block';
      } else {
          nextButton.style.display = 'block';
          submitButton.style.display = 'none';
      }
  }





      updateProgressBar();

  questions.forEach((question, index) => {
      const select = question.querySelector('select');
      if (select) {
          select.addEventListener('change', () => {
              checkAllDependencies();
          });
      }
  });


      // Verificando as dependências iniciais
      checkAllDependencies();
  });