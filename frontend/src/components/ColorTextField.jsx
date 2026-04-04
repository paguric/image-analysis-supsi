import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';

export default function MaterialNumberField({ label, color, onChange }) {
  const [value, setValue] = useState('');

  const handleKeyDown = (e) => {
    const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
    if (!allowed.includes(e.key) && !/^\d$/.test(e.key)) {
      e.preventDefault();
    }
  };

  const handleChange = (e) => {
    let newValue = e.target.value;
    if (newValue < 0)
      newValue = 0;

    setValue(newValue);
    onChange?.(Number(newValue));
  };

  return (
    <Box
      component="form"
      sx={{ '& > :not(style)': { m: 1, width: '16ch' } }}
      noValidate
      autoComplete="off"
    >

      <TextField
        label={label}
        color={color}
        focused
        type="number"
        value={value}
        onKeyDown={handleKeyDown}
        onChange={handleChange}
      />


    </Box>
  );
}