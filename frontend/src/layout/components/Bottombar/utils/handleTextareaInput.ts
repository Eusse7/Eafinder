import { resizeTextarea } from './resizeTextarea';

export function handleTextareaInput(
  textarea: HTMLTextAreaElement | null,
  setHasText: React.Dispatch<React.SetStateAction<boolean>>,
) {
  if (!textarea) {
    return;
  }

  resizeTextarea(textarea);
  setHasText(textarea.value.trim().length > 0);
}