import React from 'react';
import ReactDOM from 'react-dom';
import styled, { createGlobalStyle } from 'styled-components';

// Global styles including CSS variables
const GlobalStyle = createGlobalStyle`
  :root {
    --box-size: 100px;
    --gap: 10px;
  }

  body {
    font-family: Arial, sans-serif;
  }
`;

// Styled components
const Container = styled.div<{ columns: number; rows: number }>`
  display: grid;
  grid-template-columns: repeat(${props => props.columns}, var(--box-size));
  grid-template-rows: repeat(${props => props.rows}, var(--box-size));
  gap: var(--gap);
  justify-content: center;
  align-content: center;
  margin: 0 auto;
  border: 2px solid #000;
`;

const Box = styled.div`
  width: var(--box-size);
  height: var(--box-size);
  background-color: hsl(206deg 100% 50%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
`;

// Box component
interface BoxProps {
  number: number;
}

export const BoxComponent: React.FC<BoxProps> = ({ number }) => (
  <Box></Box>
);

// Container component
interface ContainerProps {
  columns: number;
  rows: number;
}

export const ContainerComponent: React.FC<ContainerProps> = ({ columns, rows }) => {
  const boxes = Array.from({ length: columns * rows }, (_, i) => i + 1);

  return (
    <Container columns={columns} rows={rows}>
      {boxes.map((number) => (
        <BoxComponent key={number} number={number} />
      ))}
    </Container>
  );
};


