import { GridLayout } from "./shared/components/GridLayout";

const NO_AUTH_ROUTES = ["/login"];

export const StyledContainer = (props) => {
  const { children } = props;

  if (NO_AUTH_ROUTES.includes(window.location.pathname)) {
    return <>children</>;
  }

  return <GridLayout>{children}</GridLayout>;
};
